import json
import os
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
    
    # List all calendars
    calendar_list = service.calendarList().list().execute()
    for calendar_entry in calendar_list['items']:
        cal_id = calendar_entry['id']
        cal_name = calendar_entry.get('summary')
        print(f"\nChecking Calendar: {cal_name} ({cal_id})")
        
        events_result = service.events().list(
            calendarId=cal_id, 
            timeMin=time_min,
            timeMax=time_max, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"  Start: {start}, Summary: {event.get('summary')}, Location: {event.get('location')}")

if __name__ == '__main__':
    main()
