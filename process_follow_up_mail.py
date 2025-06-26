import base64
import json
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def decode_base64(data):
    try:
        padding_needed = 4 - (len(data) % 4)
        if padding_needed and padding_needed != 4:
            data += '=' * padding_needed
        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error decoding base64 data: {e}")
        return None
        
def extract_details_from_pubsub_event(incoming_mail):
    decoded_data = decode_base64(incoming_mail['message']['data'])
    
    if not decoded_data:
        return None

    data_json = json.loads(decoded_data)
    history_id = data_json.get("historyId", None)
    email_address = data_json.get("emailAddress", None)

    return history_id, email_address

def extract_new_mails_from_history_id(history_id, credentials_info):

    creds = Credentials.from_authorized_user_info(credentials_info)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    access_token = creds.token

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "startHistoryId": history_id,
        "historyTypes": "messageAdded"
    }

    url = "https://gmail.googleapis.com/gmail/v1/users/me/history"

    response = requests.get(url, headers=headers, params=params)

    if not response.ok:
        print(f"Error: {response.status_code} {response.text}")
        return None

    history_data = response.json()
    
    if 'history' not in history_data or not history_data['history']:
        print("No new mails found in the history.")
        return []

    new_mails = []
    
    for item in history_data['history']:
        if 'messagesAdded' in item:
            for message_added in item['messagesAdded']:
                new_mails.append(message_added['message'])

    return new_mails

def extract_mail_details_from_message_id(message_id, credentials_info):
      
    def get_message_subject_and_body(message_json):
        subject = None
        body = None
    
        # Extract headers and look for Subject
        headers = message_json.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                subject = header['value']
                break
    
        # Function to recursively find plain text body
        def find_plain_text(part):
            if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                return part['body']['data']
            elif 'parts' in part:
                for sub_part in part['parts']:
                    result = find_plain_text(sub_part)
                    if result:
                        return result
            return None

        encoded_body = find_plain_text(message_json.get('payload', {}))
    
        if encoded_body:
            # Gmail API encodes message body in base64 URL safe
            decoded_bytes = base64.urlsafe_b64decode(encoded_body + '==')
            body = decoded_bytes.decode('utf-8', errors='replace')
    
        return subject, body
      
    creds = Credentials.from_authorized_user_info(credentials_info)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    access_token = creds.token

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    response = requests.get(url, headers=headers)

    if not response.ok:
        print(f"Error {response.status_code}: {response.text}")
        return None, None
    
    message = response.json()
    subject, body = get_message_subject_and_body(message)
    
    return subject, body
   
def mark_message_as_read(message_id, credentials_info):
    creds = Credentials.from_authorized_user_info(credentials_info)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    access_token = creds.token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify"
    data = {
        "removeLabelIds": ["UNREAD"]
    }

    response = requests.post(url, headers=headers, json=data)

    if not response.ok:
        print(f"Error marking message as read: {response.status_code} {response.text}")
        return False

    return True
    

# session_id = "session123"  # Example session ID, replace with actual logic to get it
# subject, body = extract_mail_details_from_pubsub_event(incoming_mail, session_id)
# print(f"Subject: {subject}")
# print(f"Body: {body}")