import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    creds_path = r"C:\Users\kehhu\AppData\Roaming\gcloud\application_default_credentials.json"
    with open(creds_path, 'r') as f:
        info = json.load(f)
    
    creds = Credentials(
        token=None,
        refresh_token=info['refresh_token'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=info['client_id'],
        client_secret=info['client_secret']
    )
    
    service = build('calendar', 'v3', credentials=creds)
    
    time_min = "2026-04-26T00:00:00Z"
    time_max = "2026-04-26T23:59:59Z"
    
    calendar_id = "e7sucjjg91p3ejku2edrqu0o7o@group.calendar.google.com" # Wenwen&Kehhua
    
    events_result = service.events().list(
        calendarId=calendar_id, 
        timeMin=time_min,
        timeMax=time_max, 
        singleEvents=True
    ).execute()
    
    print(json.dumps(events_result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
