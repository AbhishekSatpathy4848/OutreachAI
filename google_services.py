import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText


'''
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send
]
'''

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

def _get_google_service(service_name: str, version: str, access_token: str, 
                       refresh_token: str = None, client_id: str = None, 
                       client_secret: str = None, scopes: List[str] = None):
    """
    Generic function to get authenticated Google service from tokens
    
    Args:
        service_name: Name of the Google service (e.g., 'calendar', 'gmail', 'drive', 'sheets')
        version: API version (e.g., 'v3', 'v1')
        access_token: OAuth2 access token from client
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (needed for token refresh)
        client_secret: OAuth2 client secret (needed for token refresh)
        scopes: List of OAuth2 scopes (optional, defaults to SCOPES)
        
    Returns:
        Google service object
    """
    try:
        # Use provided scopes or default SCOPES
        if scopes is None:
            scopes = SCOPES
            
        # Create credentials from token
        token_info = {
            'token': access_token,
            'scopes': scopes
        }
        
        if refresh_token:
            token_info['refresh_token'] = refresh_token
        if client_id:
            token_info['client_id'] = client_id
        if client_secret:
            token_info['client_secret'] = client_secret
            
        creds = Credentials(token=access_token, 
                            refresh_token=refresh_token,
                            client_id=client_id,
                            client_secret=client_secret,
                            token_uri='https://oauth2.googleapis.com/token')
        
        # Refresh token if expired and refresh token is available
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build(service_name, version, credentials=creds)
        logger.info(f"Successfully authenticated with Google {service_name.capitalize()} API")
        return service
        
    except Exception as e:
        logger.error(f"Failed to authenticate with {service_name}: {e}")
        raise Exception(f"Authentication failed for {service_name}: {str(e)}")

def _get_calendar_service_from_token(access_token: str, refresh_token: str = None, 
                                    client_id: str = None, client_secret: str = None):
    """
    Get authenticated Google Calendar service from tokens (backward compatibility)
    
    Args:
        access_token: OAuth2 access token from client
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (needed for token refresh)
        client_secret: OAuth2 client secret (needed for token refresh)
        
    Returns:
        Google Calendar service object
    """
    return _get_google_service('calendar', 'v3', access_token, refresh_token, 
                             client_id, client_secret)

def _get_gmail_service_from_token(access_token: str, refresh_token: str = None,
                                  client_id: str = None, client_secret: str = None):
    """
    Get authenticated Gmail service from tokens (backward compatibility)
    Args:
        access_token: OAuth2 access token from client
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (needed for token refresh)
        client_secret: OAuth2 client secret (needed for token refresh)
    Returns:
        Google Gmail service object
    """
    return _get_google_service('gmail', 'v1', access_token, refresh_token,
                             client_id, client_secret)
    

def create_google_meet_meeting(
    access_token: str,
    title: str,
    start_time: str,
    duration_minutes: int = 60,
    description: str = "",
    attendees: List[str] = None,
    timezone: str = "UTC",
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> Dict[str, Any]:
    """
    Create a Google Meet meeting and add it to Google Calendar
    
    Args:
        access_token: OAuth2 access token from client authentication
        title: Meeting title
        start_time: Start time in ISO format (e.g., "2024-01-15T10:00:00")
        duration_minutes: Meeting duration in minutes (default: 60)
        description: Meeting description
        attendees: List of attendee email addresses
        timezone: Timezone (default: "UTC")
        refresh_token: OAuth2 refresh token (optional, for token refresh)
        client_id: OAuth2 client ID (optional, needed for token refresh)
        client_secret: OAuth2 client secret (optional, needed for token refresh)
    
    Returns:
        Dictionary with meeting details including Google Meet link
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Prepare attendees list
        attendees_list = []
        if attendees:
            attendees_list = [{'email': email.strip()} for email in attendees]
        
        # Create event object
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
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
        created_event = service.events().insert(
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
        
        logger.info(f"Successfully created meeting: {title}")
        return result
        
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return {
            'status': 'error',
            'error': str(error),
            'message': 'Failed to create meeting'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to create meeting'
        }


def get_upcoming_meetings(
    access_token: str,
    max_results: int = 10,
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> List[Dict[str, Any]]:
    """
    Get upcoming meetings from Google Calendar
    
    Args:
        access_token: OAuth2 access token from client authentication
        max_results: Maximum number of events to return
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        List of upcoming meeting dictionaries
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
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
                'meet_link': None,
                'description': event.get('description', ''),
                'calendar_link': event.get('htmlLink', '')
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
    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        return []

def cancel_meeting(
    access_token: str,
    event_id: str,
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> Dict[str, Any]:
    """
    Cancel a Google Calendar meeting by event ID
    
    Args:
        access_token: OAuth2 access token from client authentication
        event_id: Google Calendar event ID
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        Status dictionary
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        service.events().delete(
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
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to cancel meeting'
        }

def update_meeting(
    access_token: str,
    event_id: str,
    title: str = None,
    start_time: str = None,
    duration_minutes: int = None,
    description: str = None,
    attendees: List[str] = None,
    timezone: str = "UTC",
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> Dict[str, Any]:
    """
    Update an existing Google Calendar meeting
    
    Args:
        access_token: OAuth2 access token from client authentication
        event_id: Google Calendar event ID
        title: New meeting title (optional)
        start_time: New start time in ISO format (optional)
        duration_minutes: New duration in minutes (optional)
        description: New description (optional)
        attendees: New list of attendee email addresses (optional)
        timezone: Timezone (default: "UTC")
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        Dictionary with updated meeting details
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        # Get existing event
        existing_event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Update only provided fields
        if title is not None:
            existing_event['summary'] = title
        
        if description is not None:
            existing_event['description'] = description
            
        if start_time is not None:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            existing_event['start'] = {
                'dateTime': start_dt.isoformat(),
                'timeZone': timezone,
            }
            
            # Update end time if start time is changed
            if duration_minutes is not None:
                end_dt = start_dt + timedelta(minutes=duration_minutes)
            else:
                # Keep existing duration
                existing_end = datetime.fromisoformat(
                    existing_event['end']['dateTime'].replace('Z', '+00:00')
                )
                existing_start = datetime.fromisoformat(
                    existing_event['start']['dateTime'].replace('Z', '+00:00')
                )
                duration = existing_end - existing_start
                end_dt = start_dt + duration
                
            existing_event['end'] = {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
            }
        elif duration_minutes is not None:
            # Update only duration, keep existing start time
            start_dt = datetime.fromisoformat(
                existing_event['start']['dateTime'].replace('Z', '+00:00')
            )
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            existing_event['end'] = {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
            }
        
        if attendees is not None:
            existing_event['attendees'] = [{'email': email.strip()} for email in attendees]
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=existing_event,
            sendUpdates='all' if existing_event.get('attendees') else 'none'
        ).execute()
        
        # Extract meeting information
        result = {
            'event_id': updated_event['id'],
            'title': updated_event['summary'],
            'start_time': updated_event['start']['dateTime'],
            'end_time': updated_event['end']['dateTime'],
            'calendar_link': updated_event['htmlLink'],
            'meet_link': None,
            'attendees': [attendee['email'] for attendee in updated_event.get('attendees', [])],
            'status': 'updated'
        }
        
        # Extract Google Meet link if available
        if 'conferenceData' in updated_event:
            conference_data = updated_event['conferenceData']
            if 'entryPoints' in conference_data:
                for entry_point in conference_data['entryPoints']:
                    if entry_point['entryPointType'] == 'video':
                        result['meet_link'] = entry_point['uri']
                        break
        
        logger.info(f"Successfully updated meeting: {event_id}")
        return result
        
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return {
            'status': 'error',
            'error': str(error),
            'message': 'Failed to update meeting'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to update meeting'
        }

def get_meeting_details(
    access_token: str,
    event_id: str,
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific meeting
    
    Args:
        access_token: OAuth2 access token from client authentication
        event_id: Google Calendar event ID
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        Dictionary with meeting details
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        meeting_info = {
            'id': event['id'],
            'title': event.get('summary', 'No Title'),
            'start_time': event['start'].get('dateTime', event['start'].get('date')),
            'end_time': event['end'].get('dateTime', event['end'].get('date')),
            'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
            'description': event.get('description', ''),
            'calendar_link': event.get('htmlLink', ''),
            'meet_link': None,
            'status': event.get('status', 'confirmed')
        }
        
        # Check for Google Meet link
        if 'conferenceData' in event:
            conference_data = event['conferenceData']
            if 'entryPoints' in conference_data:
                for entry_point in conference_data['entryPoints']:
                    if entry_point['entryPointType'] == 'video':
                        meeting_info['meet_link'] = entry_point['uri']
                        break
        
        return meeting_info
        
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return {
            'status': 'error',
            'error': str(error),
            'message': 'Failed to get meeting details'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to get meeting details'
        }

def search_meetings(
    access_token: str,
    query: str,
    max_results: int = 10,
    time_min: str = None,
    time_max: str = None,
    refresh_token: str = None,
    client_id: str = None,
    client_secret: str = None
) -> List[Dict[str, Any]]:
    """
    Search for meetings in Google Calendar
    
    Args:
        access_token: OAuth2 access token from client authentication
        query: Search query string
        max_results: Maximum number of events to return
        time_min: Lower bound for search (ISO format, optional)
        time_max: Upper bound for search (ISO format, optional)
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        List of matching meeting dictionaries
    """
    try:
        # Get calendar service
        service = _get_calendar_service_from_token(
            access_token, refresh_token, client_id, client_secret
        )
        
        # Set default time_min to now if not provided
        if time_min is None:
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        search_params = {
            'calendarId': 'primary',
            'q': query,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime',
            'timeMin': time_min
        }
        
        if time_max:
            search_params['timeMax'] = time_max
        
        events_result = service.events().list(**search_params).execute()
        events = events_result.get('items', [])
        meetings = []
        
        for event in events:
            meeting_info = {
                'id': event['id'],
                'title': event.get('summary', 'No Title'),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
                'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
                'description': event.get('description', ''),
                'calendar_link': event.get('htmlLink', ''),
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
    except Exception as e:
        logger.error(f"Error searching meetings: {e}")
        return []
    
def send_email_with_token(access_token: str, to_email: str, 
                         subject: str, body_text: str, refresh_token: str,
                         client_id: str, client_secret: str):
    """
    Send an email using Gmail API with OAuth token
    
    Args:
        access_token: OAuth2 access token from client
        to_email: Recipient's email address
        subject: Email subject
        body_text: Email body (plain text)
        refresh_token: OAuth2 refresh token (optional)
        client_id: OAuth2 client ID (optional)
        client_secret: OAuth2 client secret (optional)
        
    Returns:
        Dictionary with email sending result
    """
    try:
        # Get Gmail service using the generic function
        service = _get_gmail_service_from_token(access_token=access_token, 
                                   refresh_token=refresh_token, client_id=client_id,
                                   client_secret=client_secret)

        # Create email message
        message = MIMEText(body_text)
        message['to'] = 'abhisheksatpathy4848@gmail.com'
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email
        result = service.users().messages().send(
            userId="me", 
            body={'raw': raw_message}
        ).execute()
        
        logger.info(f"✅ Email sent successfully. Message ID: {result['id']}")
        return {
            'status': 'sent',
            'message_id': result['id'],
            'to': to_email,
            'subject': subject,
            'message': 'Email sent successfully'
        }
        
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        return {
            'status': 'error',
            'error': str(error),
            'message': 'Failed to send email via Gmail API'
        }
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'message': 'Failed to send email'
        }


# Example usage for testing
if __name__ == "__main__":
    access_token = ""
    refresh_token = ""
    client_id = ""
    client_secret = ""

    result = send_email_with_token(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        to_email="recipient@example.com",
        subject="Test Email",
        body_text="This is a test email.",
        )

    #create a google meet
    # create_google_meet_meeting(
    #     access_token=access_token,
    #     refresh_token=refresh_token,
    #     client_id=client_id,
    #     client_secret=client_secret,
    #     title="Test Meeting",
    #     start_time=(datetime.now() + timedelta(days=1)).isoformat(),
    #     duration_minutes=30,
    #     description="This is a test meeting created via API.",
    #     attendees=["abhisheksatpathy4848@gmail.com"]
    # )

    # # Example: Create a meeting for tomorrow at 2 PM
    # tomorrow = datetime.now() + timedelta(days=1)
    # start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # result = create_google_meet_meeting(
    #     access_token=access_token,
    #     title="Team Standup Meeting",
    #     start_time=start_time.isoformat(),
    #     duration_minutes=30,
    #     description="Daily team standup to discuss progress and blockers",
    #     attendees=["team@example.com"],
    #     timezone="UTC"
    # )
    
    # print("Meeting Creation Result:")
    # print(json.dumps(result, indent=2))
    
    # # Get upcoming meetings
    # print("\nUpcoming Meetings:")
    # meetings = get_upcoming_meetings(access_token, max_results=5)
    # for meeting in meetings:
    #     print(f"- {meeting['title']} at {meeting['start_time']}")
    #     if meeting['meet_link']:
    #         print(f"  Meet Link: {meeting['meet_link']}")