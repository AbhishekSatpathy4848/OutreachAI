import os
from flask import Flask, render_template, request, jsonify, Response
import json
import asyncio
from datetime import datetime
import uuid
from agent import AutonomousOutreachAgent, set_display_handler, set_input_handler
import threading
from queue import Queue
import pickle

from process_follow_up_mail import extract_details_from_pubsub_event, extract_mail_details_from_message_id, extract_new_mails_from_history_id, mark_message_as_read

app = Flask(__name__)

SESSIONS_FILE = 'active_sessions.pkl'

class StreamingAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.agent = AutonomousOutreachAgent(session_id)
        self.agent.set_streaming_agent(self)  # Set reference back to streaming agent
        self.message_queue = Queue()
        self.is_active = True
        self.waiting_for_input = False
        self.pending_input_prompt = None
        
        # Set up handlers for the agent to use this streaming interface
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup handlers for display and input to work with streaming"""
        def stream_display(message):
            self.add_message('display_message', message)
        
        def stream_input(prompt, session_id):
            # Set waiting state and add the input request message
            self.waiting_for_input = True
            self.pending_input_prompt = prompt
            # self.add_message('input_request', prompt)
            # Return empty string for now - the actual input will come via the web interface
            return ""
        
        set_display_handler(stream_display)
        set_input_handler(stream_input)
        
    def add_message(self, message_type, content):
        """Add a message to the streaming queue"""
        message = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        self.message_queue.put(message)
    
    def get_messages(self):
        """Generator to yield messages from queue"""
        while self.is_active or not self.message_queue.empty():
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get(timeout=0.1)
                    yield f"data: {json.dumps(message)}\n\n"
                else:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    import time
                    time.sleep(1)
            except:
                break
                

def load_active_sessions():
    """Load active sessions from a pickle file"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    
    try:
        with open(SESSIONS_FILE, 'rb') as f:
            sessions_data = pickle.load(f)
        
        # Reconstruct StreamingAgent objects
        active_sessions = {}
        for session_id, session_data in sessions_data.items():
            streaming_agent = StreamingAgent(session_id)
            
            # Restore agent state
            if 'agent_state' in session_data:
                streaming_agent.agent.state = session_data['agent_state']
            
            # Restore streaming agent properties
            streaming_agent.is_active = session_data.get('is_active', True)
            streaming_agent.waiting_for_input = session_data.get('waiting_for_input', False)
            streaming_agent.pending_input_prompt = session_data.get('pending_input_prompt', None)
            
            active_sessions[session_id] = streaming_agent
        
        return active_sessions
    except Exception as e:
        print(f"Error loading active sessions: {e}")
        return {}

def save_active_sessions(sessions):
    """Save active sessions to a pickle file"""
    try:
        # Prepare serializable data
        sessions_data = {}
        for session_id, streaming_agent in sessions.items():
            sessions_data[session_id] = {
                'agent_state': streaming_agent.agent.state,
                'is_active': streaming_agent.is_active,
                'waiting_for_input': streaming_agent.waiting_for_input,
                'pending_input_prompt': streaming_agent.pending_input_prompt
            }
        
        with open(SESSIONS_FILE, 'wb') as f:
            pickle.dump(sessions_data, f)
    except Exception as e:
        print(f"Error saving active sessions: {e}") 

# Store active sessions
active_sessions = load_active_sessions()
print(f"Loaded {len(active_sessions)} active sessions from file.")

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    """Start a new agent session"""
    data = request.get_json()
    if data and 'campaignId' in data:
        session_id = data.get('campaignId')
    else:
        session_id = str(uuid.uuid4())
    
    # Create new streaming agent
    streaming_agent = StreamingAgent(session_id)
    active_sessions[session_id] = streaming_agent
    save_active_sessions(active_sessions)
    
    # Load previous state if exists
    streaming_agent.agent.load_state()
    
    return jsonify({
        'session_id': session_id,
        'status': 'started',
        'message': 'New outreach agent session started'
    })

@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to the agent"""
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message', '')
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    streaming_agent = active_sessions[session_id]
    
    # Add user message to stream
    streaming_agent.add_message('user_message', message)
    
    # Check if we're waiting for input
    if streaming_agent.waiting_for_input:
        # This is a response to an input request
        streaming_agent.waiting_for_input = False
        streaming_agent.pending_input_prompt = None
        
        # Continue processing with the input
        def continue_processing():
            threading.current_thread().session_id = session_id
            asyncio.run(continue_agent_processing(session_id, message))
        
        thread = threading.Thread(target=continue_processing)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'input_received', 'message': 'Continuing processing with your input'})
    else:
        # This is a new message - start processing
        def process_message():
            threading.current_thread().session_id = session_id
            asyncio.run(process_agent_message(session_id, message))
        
        thread = threading.Thread(target=process_message)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'processing'})

async def continue_agent_processing(session_id, user_input):
    """Continue agent processing after receiving user input"""
    if session_id not in active_sessions:
        return
        
    streaming_agent = active_sessions[session_id]
    agent = streaming_agent.agent
    
    try:
        # Load the saved state
        agent.load_state()
        
        # Add the user input to conversation history
        agent.state["conversation_history"].append({
            "role": "user", 
            "content": user_input
        })
        
        agent.save_state()
        
        # Continue processing with empty input to let the agent continue
        await process_agent_logic(session_id, streaming_agent, agent, "")
        
    except Exception as e:
        streaming_agent.add_message('error', f'Error continuing processing: {str(e)}')

async def process_agent_message(session_id, user_input):
    """Process initial message with the agent"""
    if session_id not in active_sessions:
        return
        
    streaming_agent = active_sessions[session_id]
    agent = streaming_agent.agent
    
    try:
        # Process the message
        await process_agent_logic(session_id, streaming_agent, agent, user_input)
        
    except Exception as e:
        streaming_agent.add_message('error', f'Error processing message: {str(e)}')

        
async def process_agent_logic(session_id, streaming_agent, agent, user_input):
    """Core agent processing logic"""
    try:
        response = await agent.get_ai_response(user_input)
        
        if response:
            # Handle case where response is a string instead of dict
            if isinstance(response, str):
                streaming_agent.add_message('agent_response', response)
                streaming_agent.add_message('completion', 'Task completed successfully!')
                return
            
            # Send thought process
            if response.get('thought'):
                streaming_agent.add_message('agent_thought', response['thought'])
            
            # Send function call info and execute if present
            if response.get('function_calls') and response['function_calls'].get('name'):
                func_name = response['function_calls']['name']
                func_inputs = response['function_calls'].get('inputs', {})
                streaming_agent.add_message('function_call', {
                    'name': func_name,
                    'inputs': func_inputs
                })
                
                # Execute the function
                function_result = await agent.execute_function(func_name, func_inputs)
                print(f"Function {func_name} executed with result: {function_result}")

                # Check if we're waiting for input (for display_to_user_and_wait_for_input)
                if func_name == "display_to_user_and_wait_for_input":
                    streaming_agent.waiting_for_input = True
                    streaming_agent.pending_input_prompt = function_result
                    streaming_agent.add_message('function_result', function_result)
                    streaming_agent.add_message('input_request', 'Waiting for your input to continue...')
                    return
                
                streaming_agent.add_message('function_result', function_result)
            
            # Continue processing if there are more function calls
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            while (response and 
                   isinstance(response, dict) and  # Add type check here
                   response.get('function_calls') and 
                   response['function_calls'].get('name') and 
                   not streaming_agent.waiting_for_input and
                   iteration < max_iterations):
                
                iteration += 1
                response = await agent.get_ai_response("")
                
                if response:
                    # Handle string response in the loop too
                    if isinstance(response, str):
                        streaming_agent.add_message('agent_response', response)
                        break
                    
                    if response.get('thought'):
                        streaming_agent.add_message('agent_thought', response['thought'])
                    
                    if response.get('function_calls') and response['function_calls'].get('name'):
                        func_name = response['function_calls']['name']
                        func_inputs = response['function_calls'].get('inputs', {})
                        streaming_agent.add_message('function_call', {
                            'name': func_name,
                            'inputs': func_inputs
                        })
                        
                        # Execute the function
                        function_result = await agent.execute_function(func_name, func_inputs)
                        
                        # Check if we're waiting for input
                        if func_name == "display_to_user_and_wait_for_input":
                            streaming_agent.waiting_for_input = True
                            streaming_agent.pending_input_prompt = function_result
                            streaming_agent.add_message('info', 'Waiting for your input to continue...')
                            return
                        
                        streaming_agent.add_message('function_result', function_result)
        
        # Send completion message if not waiting for input
        if not streaming_agent.waiting_for_input:
            streaming_agent.add_message('completion', 'Task completed successfully!')
        
    except Exception as e:
        streaming_agent.add_message('error', f'Error in agent logic: {str(e)}')

@app.route('/stream/<session_id>')
def stream_messages(session_id):
    """Stream messages for a session"""
    if session_id not in active_sessions:
        return Response('Invalid session', status=400)
    
    streaming_agent = active_sessions[session_id]
    
    def generate():
        yield "data: {\"type\": \"connected\", \"message\": \"Stream connected\"}\n\n"
        for message in streaming_agent.get_messages():
            yield message
    
    return Response(generate(), 
                   mimetype='text/event-stream',
                   headers={
                       'Cache-Control': 'no-cache',
                       'Connection': 'keep-alive',
                       'Access-Control-Allow-Origin': '*'
                   })

@app.route('/get_state/<session_id>')
def get_state(session_id):
    """Get current agent state"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    agent = active_sessions[session_id].agent
    return jsonify({
        'state': agent.state,
    })

@app.route('/end_session/<session_id>', methods=['POST'])
def end_session(session_id):
    """End an agent session"""
    if session_id in active_sessions:
        active_sessions[session_id].is_active = False
        active_sessions[session_id].agent.save_state()
        del active_sessions[session_id]
        save_active_sessions(active_sessions)
        return jsonify({'status': 'ended'})
    
    return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/get_summary/<session_id>')
def get_summary(session_id):
    """Get session summary"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    agent = active_sessions[session_id].agent
    state = agent.state
    
    summary = {
        'raw_user_query': state.get('raw_user_query', 'N/A'),
        'candidates_found': len(state.get('candidates', [])),
        'top_candidates': len(state.get('scored_candidates', [])),
        'outreach_messages': len(state.get('outreach_messages', {})),
        'meetings_scheduled': len(state.get('scheduled_meetings', [])),
        'errors': len(state.get('errors', [])),
        'function_calls': len(state.get('function_call_history', []))
    }
    
    return jsonify(summary)


@app.route('/save_oauth_credentials/<session_id>', methods=['POST'])
def save_oauth_credentials(session_id):
    """Receive and store user OAuth credentials in a JSON file"""
    data = request.get_json()
    print(data)
    credentials = data.get('credentials')
    email = data.get('email')

    credentials["token_uri"] = os.getenv("GOOGLE_TOKEN_URI")
    credentials["client_id"] = os.getenv("GOOGLE_CLIENT_ID")
    credentials["client_secret"] = os.getenv("GOOGLE_CLIENT_SECRET")

    if not session_id or not credentials or not email:
        return jsonify({'error': 'Missing session_id or credentials'}), 400
    
    final_data = {
        "email": email,
        "credentials": credentials,
    }

    # Save credentials to a file named by session_id
    try:
        with open(f'creds/creds_{session_id}.json', 'w') as f:
            json.dump(final_data, f)
        return jsonify({'status': 'success', 'message': 'Credentials saved'})
    except Exception as e:
        return jsonify({'error': f'Failed to save credentials: {str(e)}'}), 500

@app.route('/followup_email', methods=['POST'])
def followup_email():
    """Handle incoming follow-up emails and continue agent conversation"""
    incoming_mail = request.get_json()
    history_id, email_address = extract_details_from_pubsub_event(incoming_mail)

    print(f"Received follow-up emails")
    
    # might not be the right session_id, in case multiple sessions share the same email but the credentials would be the same and therefore can be used here
    credentials = None
    for file_name in os.listdir('creds'):
        session_id =  file_name.split('_')[-1].replace('.json', '')
        with open (f'creds/{file_name}', 'r') as f:
            try:
                json_data = json.load(f)
                if json_data.get('email') == email_address:
                    credentials = json_data.get('credentials')
                    break
            except json.JSONDecodeError as e:
                print(f"Error reading JSON from {file_name}: {e}")
                continue
        
    if not credentials:
        return jsonify({'message': 'Mail isn\'t a follow up mail'}), 200

    emails = extract_new_mails_from_history_id(str(int(history_id) - 500), credentials)

    filtered_emails = []
    for email in emails:
        if email.get('labelIds') and email.get('labelIds').count('INBOX') > 0 and email.get('labelIds').count('UNREAD') > 0:
            filtered_emails.append(email)
    emails = filtered_emails

    # print(f"Extracted emails: {emails}")

    if not emails or  len(emails) == 0:
        return jsonify({'error': 'No new emails found'}), 200
    
    sessions = {}
    # "session_id": [(message_id, thread_id), ...]

    for email in emails:

        message_id = email["id"]
        thread_id = email["threadId"]   

        # now we have to find the session_id based on the thread_id
        session_id_final = None

        for file_name in os.listdir('creds'):
            session_id = file_name.split('_')[-1].replace('.json', '')

            with open(f'creds/{file_name}', 'r') as f:
                try:
                    json_data = json.load(f)
                    thread_ids_sent = json_data.get('thread_ids_sent', [])
                    if thread_ids_sent and thread_id in thread_ids_sent:
                        session_id_final = session_id
                        break
                except json.JSONDecodeError as e:
                    print(f"Error reading JSON from {file_name}: {e}")
                    continue   


        if not session_id_final:
            continue

        print(f"Session ID found for thread {thread_id}: {session_id_final}")

        pairs = sessions.get(session_id_final, [])
        pairs.append((message_id, thread_id))
        sessions[session_id_final] = pairs

    if len(sessions.keys()) == 0:
        return jsonify({'message': 'Mail isn\'t a follow up mail'}), 200

    session_ids = list(sessions.keys())  # Convert to list for JSON serialization

    for session_id in session_ids:
        agent = active_sessions[session_id].agent

        mails_received_prompt = "From the emails you have sent, you have received the following follow-up emails:\n\n"

        mails_received = []

        for message_id, thread_id in sessions[session_id]:
            
            subject, body = extract_mail_details_from_message_id(message_id, credentials)

            mark_message_as_read(message_id, credentials)

            mails_received.append(f"Subject: {subject}\nContent: {body}\n\n")

            print(f"Extracted subject: {subject}, body: {body}")

            mails_received_prompt += f"Subject: {subject}\nContent: {body}\n\n"

        mails_received_prompt += "\nPlease analyze these follow-up emails and determine the appropriate response or next steps.\n\n"

        try:
            # Load the current state
            agent.load_state()
            
            # Add to conversation history
            agent.state["conversation_history"].append({
                "role": "user", 
                "content": mails_received_prompt
            })
            
            # Also track the follow-up in a separate field
            if "followup_emails" not in agent.state:
                agent.state["followup_emails"] = []
            
            agent.state["followup_emails"].extend(mails_received)
            
            agent.save_state()

            def process_message():
                threading.current_thread().session_id = session_id
                asyncio.run(process_agent_logic(session_id, active_sessions[session_id], agent, mails_received_prompt))
            
            thread = threading.Thread(target=process_message)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            active_sessions[session_id].add_message('error', f'Error processing follow-up email: {str(e)}') 

        
    return jsonify({
        'status': 'processing_followup',
        'session_ids': session_ids,
        'message': 'Follow-up email received and processing started'
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050, threaded=True)
