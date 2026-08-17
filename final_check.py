import json
import sys
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
    
    # We saw these IDs before
    calendars = [
        "primary",
        "e7sucjjg91p3ejku2edrqu0o7o@group.calendar.google.com" # Wenwen&Kehhua
    ]
    
    all_events = []
    for cal_id in calendars:
        try:
            events_result = service.events().list(
                calendarId=cal_id, 
                timeMin=time_min,
                timeMax=time_max, 
                singleEvents=True
            ).execute()
            
            cal_name = events_result.get('summary', cal_id)
            for item in events_result.get('items', []):
                all_events.append({
                    'calendar': cal_name,
                    'start': item['start'].get('dateTime', item['start'].get('date')),
                    'summary': item.get('summary'),
                    'location': item.get('location'),
                    'description': item.get('description')
                })
        except:
            pass

    # Force UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(all_events, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
