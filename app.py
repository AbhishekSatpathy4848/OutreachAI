from flask import Flask, request, jsonify
from agent import initialize_outreach_agent, run_outreach_agent
from agent_controller import AgentController

app = Flask(__name__)

# Initialize agent and state
agent, state = initialize_outreach_agent()

@app.route('/outreach', methods=['POST'])
def outreach():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' field"}), 400
    
    query = data['query']
    budget = data.get('budget', 0)
    
    # Update state with budget if provided
    global state
    if budget:
        state['budget'] = float(budget)
    
    # Run agent with query
    response, updated_state = run_outreach_agent(query, agent, state)
    
    # Update our state
    state = updated_state
    
    return jsonify({
        "response": response,
        "current_stage": state.get("current_stage"),
        "people_found": len(state.get("people_found", [])),
        "messages_sent": state.get("messages_sent", 0),
        "meetings_scheduled": len(state.get("meetings_scheduled", []))
    })

@app.route('/status', methods=['GET'])
def status():
    global state
    return jsonify({
        "current_stage": state.get("current_stage"),
        "people_found": len(state.get("people_found", [])),
        "messages_sent": state.get("messages_sent", 0),
        "meetings_scheduled": len(state.get("meetings_scheduled", []))
    })

@app.route('/', methods=['GET'])
def health_check():
    return 'OutreachAI Agent Running...', 200

def main():
    controller = AgentController()
    
    # Initial query to start the agent
    initial_query = input("Enter your initial query: ")
    controller.start_agent(initial_query)
    
    while True:
        command = input("\nEnter input for the agent, 'stop' to stop, 'restart' to restart: ")
        
        if command.lower() == 'stop':
            controller.stop_agent()
            print("Agent stopped. Enter 'restart' to start a new session.")
        elif command.lower() == 'restart':
            new_query = input("Enter a new initial query: ")
            controller.restart_agent(new_query)
        else:
            controller.provide_input(command)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
    main()