from flask import Flask, render_template, request, jsonify, Response
import json
import asyncio
from datetime import datetime
import uuid
from agent import AutonomousOutreachAgent, set_display_handler, set_input_handler
import threading
from queue import Queue

app = Flask(__name__)

# Store active sessions
active_sessions = {}

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
                

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    """Start a new agent session"""
    session_id = str(uuid.uuid4())
    
    # Create new streaming agent
    streaming_agent = StreamingAgent(session_id)
    active_sessions[session_id] = streaming_agent
    
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
            while (response and response.get('function_calls') and 
                   response['function_calls'].get('name') and 
                   not streaming_agent.waiting_for_input and
                   iteration < max_iterations):
                
                iteration += 1
                response = await agent.get_ai_response("")
                
                if response:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050, threaded=True)
