import os
from gtts import gTTS
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips

# 1. 2026/04/14 韓國財經新聞內容設定
news_items = [
    {
        "title": "KOSPI 盤中突破 6,000 點！",
        "content": "2026年4月14日，韓國股市創下歷史時刻，盤中一度摸到6000點大關。外資與機構單日掃貨超過兩兆韓元，市場信心徹底爆發！"
    },
    {
        "title": "SK海力士股價破110萬！",
        "content": "受惠於AI晶片需求噴發，SK海力士今日股價大漲6.06%，單股突破110萬3000韓元，創下歷史新高點，成為市場最強領頭羊。"
    },
    {
        "title": "IMF 逆勢看好韓國經濟！",
        "content": "在全球經濟增長放緩至3.1%之際，IMF唯獨維持韓國1.9%的成長預測。強勁的半導體出口已成為韓國經濟最強力的防波堤。"
    }
]

def create_segment(title, content, index):
    print(f"正在處理第 {index+1} 則新聞：{title}")
    
    # 生成語音 (TTS)
    audio_path = f"audio_{index}.mp3"
    tts = gTTS(text=f"{title}。{content}", lang='zh-tw')
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    
    # 建立垂直背景 (深藍色金融風格)
    bg = ColorClip(size=(1080, 1920), color=(10, 30, 60), duration=audio.duration + 0.5)
    
    # 設定字體路徑 (Windows 標準微軟正黑體)
    font_path = "C:\\Windows\\Fonts\\msjh.ttc" 
    
    # 標題文字
    title_clip = TextClip(
        title, 
        fontsize=90, 
        color='yellow', 
        font=font_path, 
        method='caption', 
        size=(900, None)
    ).set_duration(bg.duration).set_position(('center', 400))
    
    # 內容文字
    content_clip = TextClip(
        content, 
        fontsize=65, 
        color='white', 
        font=font_path, 
        method='caption', 
        size=(850, None)
    ).set_duration(bg.duration).set_position(('center', 800))
    
    # 合成片段
    segment = CompositeVideoClip([bg, title_clip, content_clip]).set_audio(audio)
    return segment, audio_path

# 主程式執行
print("--- 影片自動生成開始 ---")
segments = []
audio_files = []

for i, item in enumerate(news_items):
    seg, a_path = create_segment(item['title'], item['content'], i)
    segments.append(seg)
    audio_files.append(a_path)

# 加上結尾畫面
final_bg = ColorClip(size=(1080, 1920), color=(10, 30, 60), duration=3)
font_path = "C:\\Windows\\Fonts\\msjh.ttc"
end_text = TextClip("訂閱我們\n掌握2026全球財經", fontsize=100, color='gold', font=font_path).set_duration(3).set_position('center')
segments.append(CompositeVideoClip([final_bg, end_text]))

# 合成並輸出
final_video = concatenate_videoclips(segments, method="compose")
output_filename = "korea_finance_20260414.mp4"
final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")

# 清理暫存音訊檔
for f in audio_files:
    if os.path.exists(f):
        os.remove(f)

print(f"\n--- 影片生成成功！檔案名稱：{output_filename} ---")
