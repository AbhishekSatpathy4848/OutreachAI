# import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# from google_auth_oauthlib.flow import InstalledAppFlow


# scopes = [
#     'https://www.googleapis.com/auth/gmail.send',        # Send emails
#     'https://www.googleapis.com/auth/gmail.readonly',    # Read emails for follow-up
#     'https://www.googleapis.com/auth/calendar.readonly', # See upcoming meetings
#     'https://www.googleapis.com/auth/calendar.events',   # Create/update/cancel meetings
#     'https://www.googleapis.com/auth/gmail.modify',      # Modify emails (e.g., mark as read)
# ]

# flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes=scopes)
# creds = flow.run_local_server(port=0)

# print("Access Token:", creds.token)
# print("Refresh Token:", creds.refresh_token)
# # Refresh token if expired
# if creds.expired and creds.refresh_token:
#     creds.refresh(requests.Request())

# # Make API request (list messages as example)
# headers = {
#     'Authorization': f'Bearer {creds.token}',
# }

# response = requests.post(
#     'https://gmail.googleapis.com/gmail/v1/users/me/watch',
#     headers=headers,
#     data={
#         "labelIds": ["INBOX"],
#         "topicName": "projects/mindful-ai-e0364/topics/gmail_inbox_change"
#     }
# )

# print(response.json())

# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# import json

# # Load saved credentials JSON (this file should contain access_token, refresh_token, etc.)
# with open("creds/creds_session123.json", "r") as f:
#     info = json.load(f)["credentials"]

# print("Loaded credentials:", info)

# # Create credentials object
# creds = Credentials.from_authorized_user_info(info)

# # Check if refresh is needed
# if not creds.valid and creds.refresh_token:
#     creds.refresh(Request())
#     print("Access token refreshed:", creds.token)

# # Now you can use creds.token in your API requests


# # if user is using google services, then they should have the necessary scopes
# # For sending emails
# # For following up on emails
# # For calendar events
# # For scheduling meetings

# # For setting up Gmail hook,
# # when the user signs up for follow up emails, we will set up a webhook
# # subscribe to Gmail changes
# # and send the changes to a Pub/Sub topic
# # Now we should receive the changes in the Push endpoint

# # For every message sent we need to keep track of the message ID and thread ID
# # so that we can follow up on the email later
# # Now when we receive a change notification,
# # we need to take the historyId from the notification
# # and use that to see all newly added messages
# # once we have the new messages, decode them

# # session_id -> [(thread_id, message_id)]
# # Incoming email will be checked if it has a thread_id similar to any of the session_ids
# # If it does, we will follow up on that email

# # Huddle, Farcaster integration 
# # Connect AgentKit Agent to Outreach AI
# # Replace with AWS Bedrock
# # Finish Follow Up