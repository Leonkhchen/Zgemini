import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def try_decode(text):
    if not text:
        return text
    try:
        # The text might be wrongly interpreted as UTF-8 when it was originally Big5 or something else
        # Or it might be double-encoded. Let's try common fixes.
        return text.encode('utf-8').decode('big5', errors='ignore')
    except:
        return text

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
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    for event in events:
        summary = event.get('summary')
        location = event.get('location')
        # Print raw bytes or repr to see what's really there
        print(f"Start: {event['start'].get('dateTime')}")
        print(f"Raw Summary: {summary}")
        # print(f"Decoded Summary: {try_decode(summary)}")
        print(f"Raw Location: {location}")
        # print(f"Decoded Location: {try_decode(location)}")

if __name__ == '__main__':
    main()
