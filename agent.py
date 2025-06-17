FUNCTION_DEFINITIONS = {
    "searching_users": [
        {
            "name": "scrapeWebsiteWithSchema",
            "description": "Scrapes the given website URL using Firecrawl and extracts structured data based on a provided schema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": { "type": "string", "description": "The URL of the website to scrape." },
                    "schema": { "type": "object", "description": "A Pydantic schema (BaseModel) defining the expected structure of the extracted data." }
                },
                "required": ["url", "schema"]
            }
        },
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
            "description": "Searches for channels based on a query string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": { "type": "string", "description": "The search query for channels." },
                    "max_channels": { "type": "integer", "description": "Maximum number of channels to return.", "default": 10 }
                },
                "required": ["query"]
            }
        }
    ],

    "communication": [
        {
            "name": "send_email_with_token",
            "description": "Sends an email using an OAuth access token.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token to authenticate the email request." },
                    "sender_email": { "type": "string", "description": "The sender's email address." },
                    "to_email": { "type": "string", "description": "The recipient's email address." },
                    "subject": { "type": "string", "description": "Subject of the email." },
                    "body_text": { "type": "string", "description": "Plain text body of the email." }
                },
                "required": ["access_token", "sender_email", "to_email", "subject", "body_text"]
            }
        }
    ],

    "meet": [
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
            "name": "get_upcoming_meetings",
            "description": "Fetches upcoming meetings from the user's calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "max_results": { "type": "integer", "description": "Maximum number of meetings to return.", "default": 10 },
                    "refresh_token": { "type": "string", "description": "Optional refresh token." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token"]
            }
        },
        {
            "name": "cancel_meeting",
            "description": "Cancels a scheduled meeting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "event_id": { "type": "string", "description": "The ID of the meeting event to cancel." },
                    "refresh_token": { "type": "string", "description": "Optional refresh token." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token", "event_id"]
            }
        },
        {
            "name": "update_meeting",
            "description": "Updates the details of an existing meeting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "event_id": { "type": "string", "description": "The ID of the meeting event to update." },
                    "title": { "type": "string", "description": "New title of the meeting." },
                    "start_time": { "type": "string", "description": "New start time in ISO 8601 format." },
                    "duration_minutes": { "type": "integer", "description": "Updated duration in minutes." },
                    "description": { "type": "string", "description": "Updated description." },
                    "attendees": { "type": "array", "items": { "type": "string" }, "description": "Updated attendee list." },
                    "timezone": { "type": "string", "description": "Updated timezone.", "default": "UTC" },
                    "refresh_token": { "type": "string", "description": "Optional refresh token." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token", "event_id"]
            }
        },
        {
            "name": "get_meeting_details",
            "description": "Gets the details of a specific meeting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "event_id": { "type": "string", "description": "The ID of the meeting event." },
                    "refresh_token": { "type": "string", "description": "Optional refresh token." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token", "event_id"]
            }
        },
        {
            "name": "search_meetings",
            "description": "Searches for meetings that match the given query and time range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": { "type": "string", "description": "OAuth access token." },
                    "query": { "type": "string", "description": "Text query to search for meetings." },
                    "max_results": { "type": "integer", "description": "Maximum number of results to return.", "default": 10 },
                    "time_min": { "type": "string", "description": "ISO 8601 minimum time for filtering." },
                    "time_max": { "type": "string", "description": "ISO 8601 maximum time for filtering." },
                    "refresh_token": { "type": "string", "description": "Optional refresh token." },
                    "client_id": { "type": "string", "description": "Optional client ID." },
                    "client_secret": { "type": "string", "description": "Optional client secret." }
                },
                "required": ["access_token", "query"]
            }
        }
    ]
}

import asyncio
import json

from gemini_call import prompt_gemini
from google_search_api import google_search
from google_services import create_google_meet_meeting
from youtube_apis import search_for_channels


# States
UNDERSTAND_QUERY = "understand_query"
SEARCH_FOR_PEOPLE = "search_for_people"
REVIEW_CANDIDATES = "review_candidates"
PREPARE_OUTREACH = "prepare_outreach"
SEND_OUTREACH = "send_outreach"
SCHEDULE_MEETINGS = "schedule_meetings"

class AutonomousOutreachAgent:
    def __init__(self):
        self.conversation_history = []
        self.state = UNDERSTAND_QUERY
        self.memory = {}

    async def run(self):
        while True:
            # Compose LLM query
            llm_prompt = {
                "history": self.conversation_history,
                "current_state": self.state,
                "function_definitions": FUNCTION_DEFINITIONS,
                "goal": "Find the right people, contact them, and schedule meetings. Always ask user if you are unsure."
            }
            llm_prompt_text = json.dumps(llm_prompt, indent=2)
            
            llm_response_text = prompt_gemini(llm_prompt_text)
            print(f"🤖 LLM Response:\n{llm_response_text}\n")
            try:
                llm_response = json.loads(llm_response_text)
            except json.JSONDecodeError:
                print("⚠️ LLM response was not valid JSON. Please try again.")
                continue

            self.conversation_history.append({
                "agent_state": self.state,
                "llm_response": llm_response
            })

            # Handle LLM guidance
            if "user_prompt" in llm_response:
                user_input = input(f"🤖 {llm_response['user_prompt']} ")
                self.conversation_history.append({"user_input": user_input})
                self.memory["last_user_input"] = user_input

            if "function_to_call" in llm_response:
                func_name = llm_response["function_to_call"]
                func_inputs = llm_response.get("function_inputs", {})
                result = await self.invoke_function(func_name, func_inputs)
                self.memory["last_function_result"] = result
                self.conversation_history.append({
                    "function_call": func_name,
                    "function_inputs": func_inputs,
                    "function_result": result
                })

            # Update state
            if "next_state" in llm_response:
                self.state = llm_response["next_state"]
            else:
                print("🎉 No next state provided, exiting.")
                break

    async def invoke_function(self, func_name, inputs):
        # Replace this with actual dynamic function calls
        print(f"🛠️ Calling function: {func_name} with inputs {inputs}")
        await asyncio.sleep(1)
        return f"Simulated result of {func_name}"


    async def handle_understand_query(self):
        self.query = input("🤖 What kind of people are you looking for? Please describe: ")
        pref_input = input("💡 Any preferences (e.g., location, followers, platform)? If none, type 'none': ")
        if pref_input.strip().lower() != "none":
            self.preferences = prompt_gemini(f"Extract preferences from: {pref_input}")
        self.state = SEARCH_FOR_PEOPLE

    async def handle_search_for_people(self):
        print("🔍 Searching for candidates...")
        # Example: search both Google + channels
        google_results = google_search(self.query, num_results=5)
        channel_results = search_for_channels(self.query, max_channels=5)

        # Rank them using LLM based on user preferences
        ranking_input = f"Given the user preferences {self.preferences}, rank these candidates:\n"
        ranking_input += f"Google Results: {google_results}\nChannel Results: {channel_results}"
        ranking = prompt_gemini(ranking_input)

        self.candidates = ranking  # Simulated: you could parse or structure this better
        self.state = REVIEW_CANDIDATES

    async def handle_review_candidates(self):
        print("📝 Here are the candidates I found and ranked:\n")
        print(self.candidates)
        confirmation = input("✅ Who would you like to contact? (Provide names, links, or 'all'): ")
        if confirmation.strip().lower() == "all":
            self.selected_candidates = self.candidates
        else:
            self.selected_candidates = prompt_gemini(f"From these candidates {self.candidates}, select the ones matching: {confirmation}")
        self.state = PREPARE_OUTREACH

    async def handle_prepare_outreach(self):
        self.outreach_message = input("✉️ What message would you like to send them? (Or type 'generate' to have AI draft one): ")
        if self.outreach_message.strip().lower() == "generate":
            self.outreach_message = prompt_gemini(f"Generate a professional but friendly outreach message for: {self.query}")
        self.state = SEND_OUTREACH

    async def handle_send_outreach(self):
        print("📤 Sending outreach...")
        for candidate in self.selected_candidates:
            email = prompt_gemini(f"Extract the best email/contact for: {candidate}")
            # send_email_with_token should be called with actual params, but we'll mock
            print(f"Sending to {email}...\nMessage: {self.outreach_message}")
        self.state = SCHEDULE_MEETINGS

    async def handle_schedule_meetings(self):
        print("📅 Let’s set up meetings with interested candidates!")
        details = input("📌 Provide details: title, date/time (ISO format), duration mins, attendees (comma-separated): ")
        self.meeting_details = prompt_gemini(f"Parse meeting details from: {details}")
        # Example: create Google Meet meetings
        # meeting = create_google_meet_meeting(
        #     access_token=input("🔑 Provide your Google OAuth access token: "),
        #     title=self.meeting_details['title'],
        #     start_time=self.meeting_details['start_time'],
        #     duration_minutes=int(self.meeting_details.get('duration_minutes', 60)),
        #     attendees=self.meeting_details['attendees'].split(",")
        # )
        meeting= "test meeting"
        print(f"✅ Meeting created: {meeting}")
        self.state = None  # Finished


if __name__ == "__main__":
    agent = AutonomousOutreachAgent()
    asyncio.run(agent.run())