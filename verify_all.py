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
    
    # Range: 2026/04/26 to 2026/05/15
    time_min = "2026-04-26T00:00:00Z"
    time_max = "2026-05-15T23:59:59Z"
    
    calendar_list = service.calendarList().list().execute()
    
    all_events = []
    for entry in calendar_list.get('items', []):
        cal_id = entry['id']
        cal_name = entry.get('summary')
        
        events_result = service.events().list(
            calendarId=cal_id, 
            timeMin=time_min,
            timeMax=time_max, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        for item in events_result.get('items', []):
            start = item['start'].get('dateTime', item['start'].get('date'))
            all_events.append({
                'start': start,
                'summary': item.get('summary', '(無主旨)'),
                'location': item.get('location', ''),
                'calendar': cal_name
            })
    
    # Sort by start time
    all_events.sort(key=lambda x: x['start'])

    sys.stdout.reconfigure(encoding='utf-8')
    for e in all_events:
        print(f"{e['start'][:16]} | {e['summary']} | {e['location']}")

if __name__ == '__main__':
    main()
