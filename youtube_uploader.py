import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# 設定 API 權限
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    client_secrets_file = "client_secrets.json"
    if not os.path.exists(client_secrets_file):
        print(f"錯誤：找不到 {client_secrets_file}。請從 Google Cloud Console 下載並放入資料夾。")
        return None

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(youtube, file_path):
    print(f"正在上傳影片：{file_path} ...")
    
    body = {
        "snippet": {
            "title": "2026/04/14 韓國財經快訊：股市衝破6000點！#Shorts",
            "description": "今日重點：\n1. KOSPI 盤中突破 6,000 點大關\n2. SK海力士股價創歷史新高\n3. IMF維持韓國經濟增長預期\n\n#韓國經濟 #KOSPI #SK海力士 #2026財經 #YouTubeShorts",
            "tags": ["韓國", "財經", "KOSPI", "SK海力士", "IMF", "Shorts"],
            "categoryId": "25" # News & Politics
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"上傳進度：{int(status.progress() * 100)}%")

    print(f"影片上傳成功！影片 ID: {response['id']}")
    print(f"網址: https://www.youtube.com/watch?v={response['id']}")

if __name__ == "__main__":
    video_file = "korea_finance_20260414.mp4"
    
    if not os.path.exists(video_file):
        print(f"錯誤：找不到影片檔 {video_file}，請先執行 video_generator.py。")
    else:
        youtube_service = get_authenticated_service()
        if youtube_service:
            upload_video(youtube_service, video_file)
