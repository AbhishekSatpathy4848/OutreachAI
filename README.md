# Autonomous Outreach Agent API

A powerful AI-driven outreach automation system with real-time streaming capabilities. This agent can find, score, and prepare personalized outreach messages for potential podcast guests, influencers, co-founders, or any professional connections.

## Features

- **Autonomous Operation**: Minimal human intervention required
- **Real-time Streaming**: Live updates via Server-Sent Events
- **AI-Powered Scoring**: Intelligent candidate ranking
- **Personalized Outreach**: Custom message generation
- **Multi-platform Search**: Google, YouTube, and web scraping
- **Session Management**: Persistent state across interactions

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python app.py
   ```

3. **Access the Web Interface**
   ```
   http://localhost:5050
   ```

## API Reference

### Base URL
```
http://localhost:5050
```

### Authentication
No authentication required for local development.

---

## Session Management

### Start a Session
Initialize a new agent session.

```http
POST /start_session
Content-Type: application/json

{}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "started",
  "message": "New outreach agent session started"
}
```

### End a Session
Terminate an active session and save state.

```http
POST /end_session/{session_id}
```

**Response:**
```json
{
  "status": "ended"
}
```

---

## Real-time Streaming

### Connect to Message Stream
Establish a Server-Sent Events connection for real-time updates.

```http
GET /stream/{session_id}
Accept: text/event-stream
```

**Stream Data Format:**
```javascript
data: {
  "type": "message_type",
  "content": "message_content",
  "timestamp": "2025-06-19T12:00:00.000Z",
  "session_id": "uuid-string"
}
```

### Message Types

| Type | Description | When to Show |
|------|-------------|--------------|
| `connected` | Stream connection established | System status |
| `heartbeat` | Keep-alive message | Ignore |
| `user_message` | Echo of user's message | User bubble |
| `agent_thought` | Agent's reasoning process | Agent thinking |
| `display_message` | **Main agent messages** | **Primary content** |
| `function_call` | Function being executed | Progress indicator |
| `function_result` | Function execution result | Result summary |
| `input_request` | Agent needs user input | Enable input field |
| `completion` | Task completed successfully | Success message |
| `error` | Error occurred | Error display |
| `info` | General information | Info message |

---

## Message Handling

### Send Message to Agent
Send a user message or response to the agent.

```http
POST /send_message
Content-Type: application/json

{
  "session_id": "uuid-string",
  "message": "Find AI podcast guests with 10k+ followers and $500 budget"
}
```

**Response:**
```json
{
  "status": "processing",
  "message": "Message received and processing started"
}
```

**Status Values:**
- `processing` - New message being processed
- `input_received` - Response to input request received

---

## State Management

### Get Current Agent State
Retrieve the complete current state of the agent.

```http
GET /get_state/{session_id}
```

**Response:**
```json
{
  "state": {
    "raw_user_query": "Find AI podcast guests with 10k+ followers",
    "search_criteria": {...},
    "candidates": [...],
    "scored_candidates": [...],
    "outreach_messages": {...},
    "scheduled_meetings": [...],
    "user_preferences": {...},
    "conversation_history": [...],
    "errors": [...]
  }
}
```

### Get Session Summary
Get a high-level summary of the session progress.

```http
GET /get_summary/{session_id}
```

**Response:**
```json
{
  "raw_user_query": "Find AI podcast guests with 10k+ followers",
  "candidates_found": 25,
  "top_candidates": 10,
  "outreach_messages": 5,
  "meetings_scheduled": 0,
  "errors": 0,
  "function_calls": 8
}
```

---

## Frontend Implementation Guide

### 1. Basic Setup

```javascript
class OutreachAgentClient {
  constructor() {
    this.sessionId = null;
    this.eventSource = null;
    this.isProcessing = false;
    this.waitingForInput = false;
  }
  
  async start() {
    // Start session
    const response = await fetch('/start_session', { method: 'POST' });
    const data = await response.json();
    this.sessionId = data.session_id;
    
    // Connect to stream
    this.eventSource = new EventSource(`/stream/${this.sessionId}`);
    this.eventSource.onmessage = (event) => {
      this.handleMessage(JSON.parse(event.data));
    };
  }
}
```

### 2. Message Handling

```javascript
handleMessage(data) {
  switch(data.type) {
    case 'display_message':
      // PRIMARY: Show agent's main messages
      this.displayAgentMessage(data.content);
      break;
      
    case 'agent_thought':
      // Show agent's thinking process
      this.showThinkingIndicator(data.content);
      break;
      
    case 'function_call':
      // Show progress: "Searching Google...", "Scoring candidates..."
      this.showProgress(data.content.name, data.content.inputs);
      break;
      
    case 'function_result':
      // Show results summary
      this.showResultSummary(data.content);
      break;
      
    case 'input_request':
      // IMPORTANT: Enable input field and show request
      this.waitingForInput = true;
      this.isProcessing = false;
      this.enableInput(data.content);
      break;
      
    case 'completion':
      // Task completed - ready for new input
      this.isProcessing = false;
      this.waitingForInput = false;
      this.showCompletion(data.content);
      this.enableInput();
      break;
      
    case 'error':
      // Show error and allow retry
      this.isProcessing = false;
      this.showError(data.content);
      this.enableInput();
      break;
  }
}
```

### 3. Sending Messages

```javascript
async sendMessage(message) {
  // Prevent multiple simultaneous messages
  if (this.isProcessing && !this.waitingForInput) return;
  
  // Update state
  this.isProcessing = true;
  this.waitingForInput = false;
  
  // Show user message immediately
  this.displayUserMessage(message);
  
  // Send to backend
  try {
    await fetch('/send_message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: this.sessionId,
        message: message
      })
    });
  } catch (error) {
    this.showError('Failed to send message');
    this.isProcessing = false;
  }
}
```

### 4. UI State Management

```javascript
// Input field states
enableInput(prompt = null) {
  const inputField = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  
  inputField.disabled = false;
  sendButton.disabled = false;
  
  if (prompt) {
    inputField.placeholder = "Please respond to: " + prompt;
  } else {
    inputField.placeholder = "Enter your message...";
  }
  
  inputField.focus();
}

disableInput() {
  document.getElementById('messageInput').disabled = true;
  document.getElementById('sendButton').disabled = true;
}
```

---

## Message Content Formatting

### Display Messages (`display_message`)
These are the primary agent communications. Format them nicely:

```javascript
formatDisplayMessage(content) {
  // Add appropriate emojis
  if (content.includes('Successfully') || content.includes('✅')) {
    return '✅ ' + content;
  } else if (content.includes('Searching') || content.includes('Finding')) {
    return '🔍 ' + content;
  } else if (content.includes('Scoring') || content.includes('Analyzing')) {
    return '📊 ' + content;
  } else if (content.includes('Generated') || content.includes('Preparing')) {
    return '✍️ ' + content;
  }
  return content;
}
```

### Function Results (`function_result`)
Format results in user-friendly way:

```javascript
formatFunctionResult(result) {
  if (result.scored_candidates) {
    return `✅ Scored ${result.total_scored} candidates using ${result.method} method`;
  }
  
  if (result.outreach_messages) {
    return `📧 Generated ${result.total_prepared} personalized outreach messages`;
  }
  
  if (Array.isArray(result)) {
    return `📋 Found ${result.length} results`;
  }
  
  return JSON.stringify(result, null, 2);
}
```

---

## Example Usage Flow

### 1. Find Podcast Guests
```javascript
client.sendMessage("Find AI podcast guests with 10k+ followers, budget $500 per episode");

// Agent will:
// 1. Search Google and YouTube
// 2. Scrape candidate information
// 3. Score candidates using AI
// 4. Prepare personalized outreach messages
// 5. Present top candidates with outreach ready
```

### 2. Handle Clarification Requests
```javascript
// If agent needs clarification, you'll receive:
// type: "input_request"
// content: "I need clarification: 1. What industry focus? 2. Preferred guest location?"

// Your frontend should:
// 1. Show the questions
// 2. Enable input field
// 3. Send user's response
client.sendMessage("Technology industry, any location is fine");
```

### 3. Get Results
```javascript
// After completion, get the full state
const state = await fetch(`/get_state/${sessionId}`).then(r => r.json());

// Access results
console.log('Candidates found:', state.state.candidates.length);
console.log('Outreach messages:', state.state.outreach_messages);
```

---

## Error Handling

### Connection Errors
```javascript
eventSource.onerror = () => {
  console.log('Stream connection lost, attempting reconnect...');
  setTimeout(() => {
    this.eventSource = new EventSource(`/stream/${this.sessionId}`);
  }, 3000);
};
```

### Session Errors
```javascript
// If you receive session errors, start a new session
if (error.message.includes('Invalid session')) {
  await this.start(); // Start new session
}
```

---

## Advanced Features

### Persistent Sessions
Sessions automatically save state. You can resume a session by loading the saved state:

```javascript
// Sessions are saved as: agent_state_{session_id}.json
// The agent automatically loads previous state when starting
```

### Custom Scoring
The agent uses AI-powered scoring by default, but falls back to basic scoring if needed.

### Multi-step Workflows
The agent can handle complex multi-step processes:
1. Search for candidates
2. Score and rank them
3. Prepare outreach messages
4. Schedule meetings (if credentials provided)

---

## Configuration

### Environment Variables
```bash
# Add to your environment or .env file
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
FIRECRAWL_API_KEY=your_firecrawl_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Required Files
- `credentials.json` - Google OAuth credentials
- `creds.txt` - Additional API credentials
- `requirements.txt` - Python dependencies

---

## Troubleshooting

### Common Issues

1. **Stream Connection Issues**
   - Check if session_id is valid
   - Ensure server is running
   - Check browser console for errors

2. **Agent Not Responding**
   - Check if waiting for input (`input_request` message)
   - Verify API credentials are configured
   - Check server logs for errors

3. **Message Formatting Issues**
   - Implement proper message type handling
   - Format `display_message` content appropriately
   - Handle `function_result` objects correctly

### Debug Mode
The Flask app runs in debug mode by default. Check console output for detailed error information.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
