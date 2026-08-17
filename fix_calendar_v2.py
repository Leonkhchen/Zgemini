import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def fix_encoding(text):
    if not text: return text
    try:
        # Step 1: Recover the original raw bytes that were misidentified
        # This is complex because the API client might have already 
        # converted unknown bytes to U+FFFD (the replacement character).
        # But let's try to fetch it again and see the raw bytes if possible.
        pass
    except: return text

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
    
    # Check 4/27 09:30 specifically
    time_min = "2026-04-27T00:00:00Z"
    time_max = "2026-04-27T23:59:59Z"
    cal_id = "e7sucjjg91p3ejku2edrqu0o7o@group.calendar.google.com"
    
    events_result = service.events().list(
        calendarId=cal_id, 
        timeMin=time_min,
        timeMax=time_max, 
        singleEvents=True
    ).execute()
    
    import binascii
    for item in events_result.get('items', []):
        summary = item.get('summary', '')
        # We try to see if there's any way to get the original bytes
        # Since the API response is already a Python dict (unicode), 
        # if the transmission was UTF-8, but content was Big5, it's garbled.
        print(f"Start: {item['start'].get('dateTime')}")
        print(f"Summary: {summary}")
        # Let's try to print the unicode hex codes
        print(f"Summary Hex: {' '.join([hex(ord(c)) for c in summary])}")

if __name__ == '__main__':
    main()
