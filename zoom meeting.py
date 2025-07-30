import requests
import json
import datetime
import os
from requests.auth import HTTPBasicAuth

# Zoom API credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret_key'
REDIRECT_URI = 'your_redirect_url'

# Zoom API endpoints
TOKEN_URL = 'Url'
MEETING_URL = 'url'

# Token file
TOKEN_FILE = 'zoom_tokens.json'

# Function to load tokens from a file
def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return json.load(file)
    return {}

# Function to save tokens to a file
def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as file:
        json.dump(tokens, file)

# Function to get a new access token using the refresh token
def refresh_oauth_token(refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(TOKEN_URL, data=data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    response_data = response.json()
    if 'access_token' in response_data and 'refresh_token' in response_data:
        tokens = {
            'access_token': response_data['access_token'],
            'refresh_token': response_data['refresh_token']
        }
        save_tokens(tokens)
        return tokens
    else:
        raise Exception("Failed to refresh token: {}".format(response_data))

# Function to schedule a Zoom meeting
def schedule_meeting():
    tokens = load_tokens()
    if not tokens:
        raise Exception("No tokens found. Please authenticate first.")

    try:
        access_token = tokens['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        meeting_details = {
            'topic': 'cron job',
            'type': 2,
            'start_time': (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).isoformat() + 'Z',
            'duration': 30,
            'timezone': 'UTC',
            'agenda': 'Discuss the project updates',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'waiting_room': True,
            }
        }
        response = requests.post(MEETING_URL, headers=headers, data=json.dumps(meeting_details))
        if response.status_code == 401:  # Unauthorized
            tokens = refresh_oauth_token(tokens['refresh_token'])
            access_token = tokens['access_token']
            headers['Authorization'] = f'Bearer {access_token}'
            response = requests.post(MEETING_URL, headers=headers, data=json.dumps(meeting_details))
        return response.json()
    except Exception as e:
        print(f"Error scheduling meeting: {e}")
        return None

if __name__ == "__main__":
    meeting_info = schedule_meeting()
    if meeting_info:
        print(f"Meeting scheduled successfully: {meeting_info}")
    else:
        print("Failed to schedule the meeting. Please check the logs.")
