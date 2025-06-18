import requests
from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow


scopes = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes=scopes)
creds = flow.run_local_server(port=0)

print("Access Token:", creds.token)
print("Refresh Token:", creds.refresh_token)
# Refresh token if expired
if creds.expired and creds.refresh_token:
    creds.refresh(requests.Request())

# Make API request (list messages as example)
headers = {
    'Authorization': f'Bearer {creds.token}',
}

# response = requests.post(
#     'https://gmail.googleapis.com/gmail/v1/users/me/watch',
#     headers=headers,
#     data={
#         "labelIds": ["INBOX"],
#         "topicName": "projects/mindful-ai-e0364/topics/gmail_inbox_change"
#     }
# )

# print(response.json())