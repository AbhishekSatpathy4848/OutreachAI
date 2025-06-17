import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MeetingDetails:
    """Data class for meeting details"""
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    attendees: List[str] = None
    timezone: str = "UTC"

class GoogleMeetCalendarTool:
    """
    A tool for creating Google Meet meetings and adding them to Google Calendar.
    Designed to be used as a function tool for LLMs.
    """
    
    # OAuth 2.0 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        """
        Initialize the Google Meet Calendar Tool
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google APIs"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Calendar API")
    
    def create_meeting_with_meet(self, meeting_details: MeetingDetails) -> Dict[str, Any]:
        """
        Create a calendar event with Google Meet integration
        
        Args:
            meeting_details: MeetingDetails object with meeting information
            
        Returns:
            Dictionary containing meeting information including Meet link
        """
        try:
            # Prepare attendees list
            attendees_list = []
            if meeting_details.attendees:
                attendees_list = [{'email': email.strip()} for email in meeting_details.attendees]
            
            # Create event object
            event = {
                'summary': meeting_details.title,
                'description': meeting_details.description,
                'start': {
                    'dateTime': meeting_details.start_time.isoformat(),
                    'timeZone': meeting_details.timezone,
                },
                'end': {
                    'dateTime': meeting_details.end_time.isoformat(),
                    'timeZone': meeting_details.timezone,
                },
                'attendees': attendees_list,
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{int(datetime.now().timestamp())}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 10},       # 10 minutes before
                    ],
                },
            }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all' if attendees_list else 'none'
            ).execute()
            
            # Extract meeting information
            result = {
                'event_id': created_event['id'],
                'title': created_event['summary'],
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime'],
                'calendar_link': created_event['htmlLink'],
                'meet_link': None,
                'attendees': [attendee['email'] for attendee in created_event.get('attendees', [])],
                'status': 'created'
            }
            
            # Extract Google Meet link if available
            if 'conferenceData' in created_event:
                conference_data = created_event['conferenceData']
                if 'entryPoints' in conference_data:
                    for entry_point in conference_data['entryPoints']:
                        if entry_point['entryPointType'] == 'video':
                            result['meet_link'] = entry_point['uri']
                            break
            
            logger.info(f"Successfully created meeting: {meeting_details.title}")
            return result
            
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return {
                'status': 'error',
                'error': str(error),
                'message': 'Failed to create meeting'
            }
    
    def get_upcoming_meetings(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming meetings from calendar
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of upcoming meeting dictionaries
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            meetings = []
            
            for event in events:
                meeting_info = {
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                    'end_time': event['end'].get('dateTime', event['end'].get('date')),
                    'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
                    'meet_link': None
                }
                
                # Check for Google Meet link
                if 'conferenceData' in event:
                    conference_data = event['conferenceData']
                    if 'entryPoints' in conference_data:
                        for entry_point in conference_data['entryPoints']:
                            if entry_point['entryPointType'] == 'video':
                                meeting_info['meet_link'] = entry_point['uri']
                                break
                
                meetings.append(meeting_info)
            
            return meetings
            
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []
    
    def cancel_meeting(self, event_id: str) -> Dict[str, Any]:
        """
        Cancel a meeting by event ID
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Status dictionary
        """
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Successfully cancelled meeting: {event_id}")
            return {
                'status': 'cancelled',
                'event_id': event_id,
                'message': 'Meeting cancelled successfully'
            }
            
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return {
                'status': 'error',
                'error': str(error),
                'message': 'Failed to cancel meeting'
            }

# LLM-friendly wrapper functions
def create_google_meet_meeting(
    title: str,
    start_time: str,
    duration_minutes: int = 60,
    description: str = "",
    attendees: List[str] = None,
    timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    LLM-friendly function to create a Google Meet meeting
    
    Args:
        title: Meeting title
        start_time: Start time in ISO format (e.g., "2024-01-15T10:00:00")
        duration_minutes: Meeting duration in minutes (default: 60)
        description: Meeting description
        attendees: List of attendee email addresses
        timezone: Timezone (default: "UTC")
    
    Returns:
        Dictionary with meeting details including Google Meet link
    """
    try:
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Create meeting details
        meeting_details = MeetingDetails(
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            attendees=attendees or [],
            timezone=timezone
        )
        
        # Initialize tool and create meeting
        tool = GoogleMeetCalendarTool()
        result = tool.create_meeting_with_meet(meeting_details)
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to create meeting'
        }

def get_upcoming_google_meetings(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    LLM-friendly function to get upcoming meetings
    
    Args:
        max_results: Maximum number of meetings to return
        
    Returns:
        List of upcoming meetings
    """
    try:
        tool = GoogleMeetCalendarTool()
        return tool.get_upcoming_meetings(max_results)
    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        return []

def cancel_google_meeting(event_id: str) -> Dict[str, Any]:
    """
    LLM-friendly function to cancel a meeting
    
    Args:
        event_id: Google Calendar event ID
        
    Returns:
        Status dictionary
    """
    try:
        tool = GoogleMeetCalendarTool()
        return tool.cancel_meeting(event_id)
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to cancel meeting'
        }

# Example usage and testing
if __name__ == "__main__":
    # Example: Create a meeting for tomorrow at 2 PM
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    result = create_google_meet_meeting(
        title="Team Standup Meeting",
        start_time=start_time.isoformat(),
        duration_minutes=30,
        description="Daily team standup to discuss progress and blockers",
        attendees=["team@example.com"],
        timezone="UTC"
    )
    
    print("Meeting Creation Result:")
    print(json.dumps(result, indent=2))
    
    # Get upcoming meetings
    print("\nUpcoming Meetings:")
    meetings = get_upcoming_google_meetings(5)
    for meeting in meetings:
        print(f"- {meeting['title']} at {meeting['start_time']}")
        if meeting['meet_link']:
            print(f"  Meet Link: {meeting['meet_link']}")