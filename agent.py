FUNCTION_DEFINITIONS = [
        {
            "name": "scrapeWebsiteWithPrompt",
            "description": "Scrapes the given website URL using Firecrawl and extracts data guided by a custom prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": { "type": "string", "description": "The URL of the website to scrape." },
                    "prompt": { "type": "string", "description": "A natural language prompt instructing how to extract data." }
                },
                "required": ["url", "prompt"]
            }
        },
        {
            "name": "scrapeYoutubeAboutPage",
            "description": "Scrapes a YouTube channel's about page and extracts data using a predefined schema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": { "type": "string", "description": "The URL of the YouTube about page to scrape." }
                },
                "required": ["url"]
            }
        },
        {
            "name": "google_search",
            "description": "Performs a Google Custom Search for the given query and returns top search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": { "type": "string", "description": "The search query string." },
                    "num_results": { "type": "integer", "description": "Number of results to return.", "default": 5 }
                },
                "required": ["query"]
            }
        },
        {
            "name": "search_for_channels",
            "description": "Searches for channels on YouTube based on a query string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": { "type": "string", "description": "The search query for channels." },
                    "max_channels": { "type": "integer", "description": "Maximum number of channels to return.", "default": 10 }
                },
                "required": ["query"]
            }
        },
        {
            "name": "send_email_with_token",
            "description": "Sends an email using the Gmail API and an OAuth2 access token. Optionally refreshes the token if refresh credentials are provided.",
            "parameters": {
                "type": "object",
                "properties": {
                "access_token": {
                    "type": "string",
                    "description": "OAuth2 access token from client."
                },
                "to_email": {
                    "type": "string",
                    "description": "Recipient's email address."
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject."
                },
                "body_text": {
                    "type": "string",
                    "description": "Email body (plain text)."
                },
                "refresh_token": {
                    "type": "string",
                    "description": "OAuth2 refresh token (optional).",
                },
                "client_id": {
                    "type": "string",
                    "description": "OAuth2 client ID (optional).",
                },
                "client_secret": {
                    "type": "string",
                    "description": "OAuth2 client secret (optional).",
                }
                },
                "required": [
                "access_token",
                "to_email",
                "subject",
                "body_text",
                "refresh_token",
                "client_id",
                "client_secret"
                ]
            }
            },
        {
            "name": "create_google_meet_meeting",
            "description": "Creates a Google Meet meeting and returns the meeting details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "title": { "type": "string", "description": "Title of the meeting." },
                    "start_time": { "type": "string", "description": "Start time in ISO 8601 format." },
                    "duration_minutes": { "type": "integer", "description": "Duration of the meeting in minutes.", "default": 60 },
                    "description": { "type": "string", "description": "Description of the meeting.", "default": "" },
                    "attendees": { "type": "array", "items": { "type": "string" }, "description": "List of attendee email addresses." },
                    "timezone": { "type": "string", "description": "Time zone for the meeting.", "default": "UTC" },
                    "refresh_token": { "type": "string", "description": "Optional refresh token for token renewal." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token", "title", "start_time"]
            }
        },
        {
            "name": "display_to_user",
            "description": "Displays a message to the user without expecting any response. Use this for sharing information, updates, or results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": { "type": "string", "description": "The message to display to the user." }
                },
                "required": ["message"]
            }
        },
        {
            "name": "display_to_user_and_wait_for_input",
            "description": "Displays a message to the user and waits for their input to continue. Use this when you need user interaction to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": { "type": "string", "description": "The message to display to the user before waiting for input." },
                    "prompt": { "type": "string", "description": "Optional prompt text to guide user input.", "default": "Please provide your response:" }
                },
                "required": ["message"]
            }
        },
        {
            "name": "score_candidates",
            "description": "Scores and ranks a list of candidates based on user preferences and query relevance using AI analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidates": {
                        "type": "array",
                        "description": "List of candidate objects to score."
                    },
                    "user_query": {
                        "type": "string",
                        "description": "The original user query describing what they're looking for."
                    },
                    "user_preferences": {
                        "type": "object",
                        "description": "User preferences including budget, location, experience level, etc."
                    }
                },
                "required": ["candidates", "user_query"]
            }
        },
        {
            "name": "prepare_outreach",
            "description": "Prepares personalized outreach messages for scored candidates using AI to generate compelling, customized emails.",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidates": {
                        "type": "array",
                        "description": "List of scored candidate objects to prepare outreach for."
                    },
                    "user_query": {
                        "type": "string",
                        "description": "The original user query describing what they're looking for."
                    },
                    "user_preferences": {
                        "type": "object",
                        "description": "User preferences including budget, company info, etc."
                    },
                    "sender_info": {
                        "type": "object",
                        "description": "Sender information including name, company, email, etc."
                    }
                },
                "required": ["candidates", "user_query"]
            }
        },
        {
            "name": "fetch_credentials",
            "description": "Fetches OAuth credentials from a file.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "make_crypto_actions",
            "description": "Executes various crypto actions using the Coinbase AgentKit, such as receiving wallet details, checking balances, and transferring tokens(native or ERC20 tokens). You'll be using only two ERC-20 tokens here: USDC or EURC, nothing else. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": { "type": "string", "description": "The prompt describing the crypto action to perform in Natural Language." }
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "update_available_budget",
            "description": "Updates the available budget left for outreach.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_budget": { "type": "number", "description": "The new budget amount left." }
                },
                "required": ["new_budget"]
            }
        }
    ]

INITIAL_PROMPT = f'''
You are a highly autonomous outreach agent. Your primary goal is to find and connect with the right people for various purposes (e.g., podcast guests, influencers, co-founders) with minimal user intervention. You will automate the entire process from search to outreach.

Here are the functions you can use: {FUNCTION_DEFINITIONS}

You must always reply in a JSON format with the following structure:
{{
    "thought": "Your thought process on what to do next. Be concise.",
    "function_calls": {{
        "name": "function_name",
        "inputs": {{
            "param1": "value1",
            "param2": "value2"
        }}
}}
}}

**Guiding Principles for Autonomy:**
1.  **Act Independently:** Your main objective is to achieve the user's goal without asking for help.
2.  **Assume and Proceed:** Based on the initial query, make logical assumptions about user preferences (e.g., budget, location, experience level) to avoid unnecessary questions.
3.  **Clarify Only When Blocked:** Only use the `display_to_user_and_wait_for_input` function as a last resort when you are completely blocked and cannot proceed with the task.
4.  **Proactive Execution:** Use all available tools to gather a comprehensive list of candidates. Score them, prepare outreach messages, and present the results.
5.  **Clarify When Necessary:** If you need to clarify something, please ask the user, don't email or message anyone without having the mail reviewed by the user.

If there is no function call, return an empty dict for "function_calls".
Your goal is maximum automation and minimal human intervention.

ALWAYS REPLY IN A JSON FORMAT AS DESCRIBED ABOVE, EVEN IF THERE IS AN ERROR OR ANYTHING
IN CASE YOU NEED IT, THE CONTRACT ADDRESS OF USDC IS `0x036CbD53842c5426634e7929541eC2318f3dCF7e` AND THE CONTRACT ADDRESS OF EURC IS `0x808456652fdb597867f38412077A9182bf77359F`
SEE EVERY FUNCTION CALL U MAKE COSTS MONEY, COZ WE ARE USING AN API FOR IT, MINIMISE IT
'''

import asyncio
import json
import json
import asyncio

from agentkit import make_crypto_actions
from prompt_llms import prompt_gemini
from google_search_api import google_search
from google_services import create_google_meet_meeting, get_upcoming_meetings, send_email_with_token
from youtube_apis import search_for_channels
from firecrawl_search import scrapeWebsiteWithPrompt, scrapeYoutubeAboutPage

def to_json(json_string):
    try:
        first_curly_index = json_string.find("{")
        last_curly_index = json_string.rfind("}")
        result = json_string[first_curly_index:last_curly_index+1]
        json_string = json.loads(result)
        return json_string
    except:
        print("Error parsing JSON!!")


# Global handlers for display and input - can be overridden for web interface
_display_handler = None
_input_handler = None

def set_display_handler(handler):
    """Set custom display handler for web interface"""
    global _display_handler
    _display_handler = handler

def set_input_handler(handler):
    """Set custom input handler for web interface"""
    global _input_handler
    _input_handler = handler

def display_to_user(message):
    """Displays a message to the user without expecting response"""
    if _display_handler:
        _display_handler(message)
    else:
        print(f"💬 {message}")
    return message

def display_to_user_and_wait_for_input(message, prompt="Please provide your response:", session_id=None):
    """Displays a message to the user and waits for their input to continue"""
    full_message = f"{message}\n\n{prompt}"
    
    if _input_handler and session_id:
        _input_handler(full_message, session_id)
        return full_message
    else:
        print(f"💬 {message}")
        user_response = input(f"{prompt} ").strip()
        return user_response

def fetch_credentials(session_id):
    try:
        with open(f"creds/creds_{session_id}.json", "r") as f:
            json_data = json.load(f)
        return json_data["credentials"]
    except FileNotFoundError:
        return ["No credentials file found"]
    except json.JSONDecodeError as e:
        print(f"Error parsing credentials JSON: {e}")
        return ["Invalid credentials file format"]
    except Exception as e:
        print(f"Error reading credentials: {e}")
        return ["Error reading credentials file"]


class AutonomousOutreachAgent:
    def __init__(self, session_id=None):
        self.session_id = session_id
        self.streaming_agent = None  # Will be set by Flask app
        self.state = {
            "raw_user_query": "",
            "search_criteria": {},
            "budget_left": None,
            "candidates": [],
            "scored_candidates": [],
            "outreach_messages": {},
            "scheduled_meetings": [],
            "user_preferences": {},
            "budget_left": 0,
            "errors": [],
            "conversation_history": [],
        }

        self.state["conversation_history"] = [
            {
                "role": "system",
                "content": INITIAL_PROMPT
            }
        ]
    
    def set_streaming_agent(self, streaming_agent):
        """Set the streaming agent for web interface"""
        self.streaming_agent = streaming_agent
        
    def save_state(self, filename=None):
        """Save current state to file"""
        if filename is None:
            filename = f"agent_state/agent_state_{self.session_id}.json" if self.session_id else "agent_state/agent_state.json"
        with open(filename, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_state(self, filename=None):
        """Load state from file"""
        if filename is None:
            filename = f"agent_state/agent_state_{self.session_id}.json" if self.session_id else "agent_state/agent_state.json"
        try:
            with open(filename, 'r') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            print(f"No previous state found for session {self.session_id}, starting fresh.")
    
    async def execute_function(self, function_name, inputs):
        """Execute a function call and return the result"""
        try:
            if function_name == "display_to_user_and_wait_for_input":
                # For streaming interface, we need to wait for user input
                message = inputs.get("message", "")
                prompt = inputs.get("prompt", "Please provide your response:")
                if self.streaming_agent:
                    # We're in a streaming context - trigger the input request
                    result = display_to_user_and_wait_for_input(message, prompt, self.session_id)
                    # The streaming agent will handle the waiting state
                    return result
                else:
                    # Non-streaming context - use regular input
                    return display_to_user_and_wait_for_input(message, prompt)
            elif function_name == "display_to_user":
                display_to_user(inputs["message"])
                return "Message displayed"
            elif function_name == "google_search":
                return google_search(inputs["query"], inputs.get("num_results", 5))
            elif function_name == "search_for_channels":
                return search_for_channels(inputs["query"], inputs.get("max_channels", 10))
            elif function_name == "scrapeWebsiteWithPrompt":
                return await scrapeWebsiteWithPrompt(inputs["url"], inputs["prompt"])
            elif function_name == "scrapeYoutubeAboutPage":
                return await scrapeYoutubeAboutPage(inputs["url"])
            elif function_name == "send_email_with_token":
                response = send_email_with_token(**inputs)
                if response.get("status") == "sent":
                    thread_id = response.get("thread_id")
                    
                    # Read, modify, and write back the credentials file
                    creds_file_path = f"creds/creds_{self.session_id}.json"
                    try:
                        with open(creds_file_path, "r") as f:
                            json_data = json.load(f)
                        
                        if "thread_ids_sent" not in json_data:
                            json_data["thread_ids_sent"] = []
                        json_data["thread_ids_sent"].append(thread_id)
                        
                        with open(creds_file_path, "w") as f:
                            f.write(json.dumps(json_data, indent=2))
                    except Exception as e:
                        print(f"Error updating credentials file: {e}")

                return response
            elif function_name == "create_google_meet_meeting":
                return create_google_meet_meeting(**inputs)
            elif function_name == "get_upcoming_meetings":
                return get_upcoming_meetings(**inputs)
            elif function_name == "score_candidates":
                return await self.score_candidates_with_llm(
                    inputs["candidates"], 
                    inputs["user_query"], 
                    inputs.get("user_preferences", {})
                )
            elif function_name == "prepare_outreach":
                return await self.prepare_outreach_with_llm(
                    inputs["candidates"],
                    inputs["user_query"],
                    inputs.get("user_preferences", {}),
                    inputs.get("sender_info", {})
                )
            elif function_name == "fetch_credentials":
                return fetch_credentials(self.session_id)
            elif function_name == "make_crypto_actions":
                return make_crypto_actions(inputs["prompt"])
            elif function_name == "update_available_budget":
                return self.update_available_budget(inputs.get("new_budget"))
            else:
                return f"Unknown function: {function_name}"
        except Exception as e:
            error_details = f"Error executing {function_name}: {str(e)}"
            self.state["errors"].append(error_details)
            self.save_state()
            return error_details
    
    async def get_ai_response(self, user_input=""):
        """Get AI response and execute any function calls"""

        if user_input != None and len(user_input) > 0: 
            self.state["conversation_history"].append({
                "role": "user",
                "content": user_input
            })
            if not self.state.get("raw_user_query"):
                self.update_state("raw_user_query", user_input)

        context = f"""
        Context:
        Conversation history: {json.dumps(self.state["conversation_history"], indent=2)} \n

        """

        try:
            response = prompt_gemini(context)
            parsed_response = to_json(response)

            self.state["conversation_history"].append({
                "role": "assistant",
                "content": parsed_response
            })

            if not parsed_response:
                return "Error: Could not parse AI response"
            
            # Store the thought
            thought = parsed_response.get("thought", "")
            
            # Execute function calls if any
            function_calls = parsed_response.get("function_calls", {})
            function_result = None
            
            if function_calls and function_calls.get("name"):

                # print("Thought:", thought)
                # print(f"Executing function: {function_calls['name']} with inputs: {function_calls.get('inputs', {})}")
                # print()
                function_result = await self.execute_function(
                    function_calls["name"], 
                    function_calls.get("inputs", {})
                )


                # Update state based on function call
                if function_calls["name"] in ["google_search", "search_for_channels"]:
                    # Assuming these return a list of candidates
                    if isinstance(function_result, list):
                        self.state["candidates"].extend(function_result)
                elif function_calls["name"] == "score_candidates":
                    if isinstance(function_result, dict) and "scored_candidates" in function_result:
                        self.state["scored_candidates"] = function_result["scored_candidates"]
                elif function_calls["name"] == "prepare_outreach":
                     if isinstance(function_result, dict) and "outreach_messages" in function_result:
                        self.state["outreach_messages"] = function_result["outreach_messages"]

                self.save_state() # Save state after every function call

                self.state["conversation_history"].append({
                    "role": "user",
                    "content": f"Executed function: {function_calls['name']} and received result: {function_result}"
                })
            
            return {
                "thought": thought,
                "function_result": function_result,
                "function_calls": function_calls
            }
            
        except Exception as e:
            return f"Error getting AI response: {str(e)}"

    def update_available_budget(self, new_budget:int):
        """Update the available budget balance"""
        self.state["budget_left"] = new_budget
        self.save_state()
        return f"Available budget updated to {new_budget}"

    async def score_candidates_with_llm(self, candidates, user_query, user_preferences=None):
        """
        Score and rank candidates using LLM-based analysis.

        Args:
            candidates: List of candidate objects
            user_query: The original user query describing what they're looking for
            user_preferences: Dict containing user preferences (budget, location, etc.)

        Returns:
            List of scored and ranked candidates
        """
        if not candidates:
            return []

        if user_preferences is None:
            user_preferences = self.state.get("user_preferences", {})
            
        print(f"📊 Scoring {len(candidates)} candidates using AI analysis...")

        # Prepare the scoring prompt for the LLM
        scoring_prompt = f"""
        You are an expert recruiter and talent evaluator. Please analyze and score the following candidates based on the user's requirements.

        USER QUERY: {user_query}

        USER PREFERENCES:
        {json.dumps(user_preferences, indent=2)}

        CANDIDATES TO SCORE:
        {json.dumps(candidates, indent=2)}

        Please analyze each candidate and provide:
        1. A relevance score from 0-100 (100 being perfect match)
        2. Key strengths that match the requirements
        3. Potential concerns or gaps
        4. A brief reasoning for the score

        Consider the following factors:
        - Relevance to the user's query and requirements
        - Experience level and expertise
        - Audience size and engagement (if applicable)
        - Location preferences (if specified)
        - Budget constraints and typical rates
        - Overall fit for the intended purpose

        Return your response as a JSON object with this structure:
        {{
            "scored_candidates": [
                {{
                    "candidate_index": 0,
                    "score": 85,
                    "strengths": ["Strong expertise in X", "Large engaged audience"],
                    "concerns": ["May be above budget", "Location mismatch"],
                    "reasoning": "Brief explanation of the score"
                }},
                ...
            ],
            "ranking_summary": "Brief summary of the overall ranking rationale"
        }}
        """

        try:
            # Get LLM response
            llm_response = prompt_gemini(scoring_prompt)
            
            # Parse the LLM response
            scoring_result = to_json(llm_response)
            
            if not scoring_result or "scored_candidates" not in scoring_result:
                # Fallback to basic scoring if LLM fails
                print("⚠️ LLM scoring failed, using basic scoring method")
                return await self.score_candidates_basic(candidates, user_query, user_preferences)
            
            # Apply scores to candidates
            scored_candidates = []
            for score_data in scoring_result["scored_candidates"]:
                candidate_index = score_data["candidate_index"]
                if 0 <= candidate_index < len(candidates):
                    candidate = candidates[candidate_index].copy()
                    candidate["ai_score"] = score_data["score"]
                    candidate["ai_strengths"] = score_data.get("strengths", [])
                    candidate["ai_concerns"] = score_data.get("concerns", [])
                    candidate["ai_reasoning"] = score_data.get("reasoning", "")
                    scored_candidates.append(candidate)
            
            # Sort by AI score
            scored_candidates.sort(key=lambda x: x.get("ai_score", 0), reverse=True)
            
            # Apply budget constraints if specified
            max_candidates = user_preferences.get("max_candidates", 10)
            if max_candidates:
                scored_candidates = scored_candidates[:max_candidates]
            
            # Update state
            self.update_state("scored_candidates", scored_candidates)
            
            # Display results
            print(f"✅ Successfully scored {len(scored_candidates)} candidates")
            print(f"📈 Ranking Summary: {scoring_result.get('ranking_summary', 'No summary provided')}")
            
            # Show top candidates
            print("\n🏆 TOP CANDIDATES:")
            for i, candidate in enumerate(scored_candidates[:5], 1):
                print(f"{i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('ai_score', 0)}")
                if candidate.get('ai_strengths'):
                    print(f"   Strengths: {', '.join(candidate['ai_strengths'])}")
                if candidate.get('ai_concerns'):
                    print(f"   Concerns: {', '.join(candidate['ai_concerns'])}")
                print(f"   Reasoning: {candidate.get('ai_reasoning', 'No reasoning provided')}")
                print("")
            
            return {
                "scored_candidates": scored_candidates,
                "total_scored": len(scored_candidates),
                "ranking_summary": scoring_result.get('ranking_summary', ''),
                "method": "llm_based"
            }
            
        except Exception as e:
            print(f"⚠️ Error in LLM scoring: {str(e)}")
            print("Falling back to basic scoring method")
            return await self.score_candidates_basic(candidates, user_query, user_preferences)

    async def score_candidates_basic(self, candidates, user_query, user_preferences=None):
        """
        Basic scoring method as fallback when LLM scoring fails.
        """
        if not candidates:
            return []

        print("📊 Using basic scoring method...")

        scored_candidates = []
        for i, candidate in enumerate(candidates):
            candidate_copy = candidate.copy()
            
            # Basic scoring based on available data
            score = 50  # Base score
            
            # Score based on name/title relevance
            name = candidate.get('name', '').lower()
            description = candidate.get('description', '').lower()
            query_words = user_query.lower().split()
            
            for word in query_words:
                if word in name or word in description:
                    score += 10
            
            # Score based on subscriber/follower count
            subscribers = candidate.get('subscribers', 0)
            if isinstance(subscribers, (int, float)) and subscribers > 0:
                if subscribers > 100000:
                    score += 20
                elif subscribers > 10000:
                    score += 15
                elif subscribers > 1000:
                    score += 10
            
            # Cap the score at 100
            score = min(score, 100)
            
            candidate_copy["ai_score"] = score
            candidate_copy["ai_strengths"] = ["Basic scoring applied"]
            candidate_copy["ai_concerns"] = ["Limited analysis available"]
            candidate_copy["ai_reasoning"] = "Basic scoring based on keyword matching and audience size"
            
            scored_candidates.append(candidate_copy)

        # Sort by score
        scored_candidates.sort(key=lambda x: x.get("ai_score", 0), reverse=True)

        return {
            "scored_candidates": scored_candidates,
            "total_scored": len(scored_candidates),
            "ranking_summary": "Basic scoring applied due to LLM unavailability",
            "method": "basic"
        }
    

    async def prepare_outreach_with_llm(self, candidates, user_query, user_preferences=None, sender_info=None):
            """
            Prepare personalized outreach messages using LLM-powered content generation.
            
            Args:
                candidates: List of candidate objects to prepare outreach for
                user_query: The original user query describing what they're looking for
                user_preferences: Dict containing user preferences (budget, location, etc.)
                sender_info: Dict containing sender information (name, company, etc.)
            
            Returns:
                Dictionary with prepared outreach messages
            """
            if not candidates:
                return {"error": "No candidates provided", "outreach_messages": {}}
            
            if user_preferences is None:
                user_preferences = self.state.get("user_preferences", {})
            
            if sender_info is None:
                sender_info = self.state.get("sender_info", {})
                
            print(f"✍️ Preparing personalized outreach messages for {len(candidates)} candidates using AI...")
            
            outreach_messages = {}
            
            for i, candidate in enumerate(candidates, 1):
                try:
                    print(f"📝 Generating message {i}/{len(candidates)}: {candidate.get('name', 'Unknown')}")
                    
                    # Create comprehensive prompt for LLM
                    outreach_prompt = f"""
                    You are an expert outreach specialist. Create a highly personalized and compelling outreach email.

                    CONTEXT:
                    User Query: {user_query}
                    
                    SENDER INFORMATION:
                    {json.dumps(sender_info, indent=2)}
                    
                    USER PREFERENCES:
                    {json.dumps(user_preferences, indent=2)}
                    
                    CANDIDATE DETAILS:
                    Name: {candidate.get('name', 'Unknown')}
                    Description: {candidate.get('description', 'No description available')}
                    URL: {candidate.get('url', 'No URL available')}
                    Source: {candidate.get('source', 'Unknown')}
                    AI Score: {candidate.get('ai_score', 'N/A')}
                    AI Strengths: {candidate.get('ai_strengths', [])}
                    Subscribers/Followers: {candidate.get('subscribers', 'Unknown')}
                    
                    REQUIREMENTS:
                    1. Create a personalized email that doesn't sound generic
                    2. Reference specific details about the candidate's work/expertise
                    3. Clearly explain the opportunity and value proposition
                    4. Include relevant budget/compensation information if available
                    5. Make it professional but warm and engaging
                    6. Include a clear call-to-action
                    7. Keep it concise but compelling (2-3 paragraphs max)
                    
                    Return your response as a JSON object with this structure:
                    {{
                        "subject": "Compelling subject line",
                        "body": "Full email body with personalization",
                        "key_personalization": "Brief note about what made this personal",
                        "call_to_action": "The specific action you want them to take"
                    }}
                    
                    Make sure the email feels authentic and specifically tailored to this candidate based on their background and the user's needs.
                    """
                    
                    # Get LLM response
                    llm_response = prompt_gemini(outreach_prompt)
                    
                    # Parse the LLM response
                    try:
                        message_data = to_json(llm_response)
                        
                        if not message_data or "subject" not in message_data:
                            # Fallback to basic template
                            message_data = self._create_basic_outreach_template(candidate, user_query, user_preferences, sender_info)
                            
                    except Exception as parse_error:
                        print(f"⚠️ Error parsing LLM response for {candidate.get('name', 'Unknown')}: {parse_error}")
                        message_data = self._create_basic_outreach_template(candidate, user_query, user_preferences, sender_info)
                    
                    # Add candidate info to message
                    message_data["candidate"] = candidate
                    message_data["candidate_name"] = candidate.get('name', 'Unknown')
                    message_data["candidate_email"] = candidate.get('email', '')
                    message_data["candidate_contact"] = candidate.get('contact_info', {})
                    message_data["generated_method"] = "llm"
                    
                    # Store the message
                    outreach_messages[candidate.get('name', f'Candidate_{i}')] = message_data
                    
                    print(f"✅ Generated personalized message for {candidate.get('name', 'Unknown')}")
                    
                except Exception as e:
                    print(f"❌ Error generating message for {candidate.get('name', 'Unknown')}: {str(e)}")
                    # Create fallback message
                    fallback_message = self._create_basic_outreach_template(candidate, user_query, user_preferences, sender_info)
                    fallback_message["candidate"] = candidate
                    fallback_message["generated_method"] = "fallback"
                    outreach_messages[candidate.get('name', f'Candidate_{i}')] = fallback_message
            
            # Update state
            self.update_state("outreach_messages", outreach_messages)
            
            # Display summary
            print(f"📧 Successfully prepared {len(outreach_messages)} personalized outreach messages")
            print("\n📋 OUTREACH MESSAGES SUMMARY:")
            for name, msg_data in list(outreach_messages.items())[:3]:  # Show first 3
                print(f"\n👤 {name}:")
                print(f"   Subject: {msg_data.get('subject', 'No subject')}")
                print(f"   Personalization: {msg_data.get('key_personalization', 'None')}")
                print(f"   Method: {msg_data.get('generated_method', 'unknown')}")
                
            if len(outreach_messages) > 3:
                print(f"\n... and {len(outreach_messages) - 3} more messages")
            
            return {
                "status": "success",
                "outreach_messages": outreach_messages,
                "total_prepared": len(outreach_messages),
                "message": f"Successfully prepared {len(outreach_messages)} personalized outreach messages"
            }
        
    def _create_basic_outreach_template(self, candidate, user_query, user_preferences, sender_info):
            """Create a basic outreach template as fallback"""
            sender_name = sender_info.get('name', 'Our Team')
            company_name = sender_info.get('company', 'Our Company')
            budget_info = user_preferences.get('budget', 'Competitive compensation')
            
            subject = f"Collaboration Opportunity - {user_query}"
            
            body = f"""Hi {candidate.get('name', 'there')},

            I hope this email finds you well. I came across your work and was impressed by your expertise in {user_query}.

            I'm {sender_name} from {company_name}, and I'm reaching out regarding an opportunity that I believe would be a great fit for your background and expertise.

            {user_query}

            We're offering {budget_info} and would love to discuss this further with you.

            Would you be interested in a brief conversation to explore this opportunity?

            Best regards,
            {sender_name}
            {company_name}"""
                    
            return {
                "subject": subject,
                "body": body,
                "key_personalization": "Basic template with candidate name and expertise area",
                "call_to_action": "Brief conversation to explore opportunity",
                "generated_method": "template"
            }

    async def prepare_outreach(self):
        """Legacy method for backward compatibility"""
        candidates = self.state.get("scored_candidates", [])
        user_query = self.state.get("search_criteria", {}).get("query", "")
        user_preferences = self.state.get("user_preferences", {})
        sender_info = self.state.get("sender_info", {})
        
        if not candidates:
            print("❌ No scored candidates found. Please score candidates first.")
            return "No candidates to prepare outreach for"
        
        result = await self.prepare_outreach_with_llm(candidates, user_query, user_preferences, sender_info)
        
        if result["status"] == "success":
            print("✅ Outreach preparation completed successfully")
            return f"Successfully prepared {result['total_prepared']} outreach messages"
        else:
            return f"Error preparing outreach: {result.get('message', 'Unknown error')}"
        
    def update_state(self, key, value):
        """Update a specific state key"""
        self.state[key] = value
        self.save_state()
        
    async def run_agent(self, user_input=""):
        """Run the agent with the provided user input"""
        self.load_state()
        while True:
            response = await self.get_ai_response(user_input)
            if not response or not response.get("function_calls") or len(response.get("function_calls", {}).keys()) == 0:
                break
            if response.get("function_calls").get("name") == "display_to_user_and_wait_for_input":
                return response.get("function_calls").get("inputs", {}).get("message", "")
        self.save_state()
        return self.state
    
# Main execution
async def main():
    agent = AutonomousOutreachAgent(session_id="session_12345")  # Example session ID
    await agent.run_agent("hello")

if __name__ == "__main__":
    asyncio.run(main())
