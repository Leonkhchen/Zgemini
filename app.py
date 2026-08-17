import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="Zgemini Cloud Hub with Google AI Pro")

# 讀取 Google AI Studio API Key (支援 AI Pro 配額)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PromptRequest(BaseModel):
    prompt: str

# Health check endpoint for Cloud Run
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Zgemini Cloud Run Hub",
        "gemini_api_configured": bool(GEMINI_API_KEY)
    }

# Gemini AI 呼叫端點 (消耗您的 Google AI 帳號額度)
@app.post("/api/generate")
def generate_text(req: PromptRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="GEMINI_API_KEY 未設定。請在環境變數中設定來自 Google AI Studio 的 API Key。"
        )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(req.prompt)
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static web projects if they exist
static_projects = ["wang-yangming-chat", "conference-website", "pomodoro-timer", "news-highlights"]
for proj in static_projects:
    if os.path.exists(proj) and os.path.isdir(proj):
        app.mount(f"/{proj}", StaticFiles(directory=proj, html=True), name=proj)

@app.get("/", response_class=HTMLResponse)
def index():
    links_html = ""
    for proj in static_projects:
        if os.path.exists(proj):
            links_html += f'<li><a href="/{proj}/" style="color: #2563eb; text-decoration: none; font-size: 1.1rem; font-weight: 500;">🚀 {proj}</a></li>\n'

    ai_status_badge = (
        '<span style="background: #dcfce7; color: #166534; padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">● Gemini API 已連線</span>'
        if GEMINI_API_KEY else
        '<span style="background: #fef9c3; color: #854d0e; padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;">○ Gemini API 待設定 (可傳入 GEMINI_API_KEY)</span>'
    )

    return f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zgemini Cloud Hub</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f8fafc;
                color: #1e293b;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            .card {{
                background: white;
                padding: 2.5rem;
                border-radius: 1rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                max-width: 520px;
                width: 90%;
            }}
            h1 {{
                font-size: 1.75rem;
                margin-bottom: 0.5rem;
                color: #0f172a;
            }}
            p {{
                color: #64748b;
                margin-bottom: 1.5rem;
                line-height: 1.5;
            }}
            ul {{
                list-style: none;
                padding: 0;
                margin: 0 0 1.5rem 0;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }}
            li {{
                padding: 0.75rem 1rem;
                background: #f1f5f9;
                border-radius: 0.5rem;
                transition: background 0.2s;
            }}
            li:hover {{
                background: #e2e8f0;
            }}
            .status-group {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-bottom: 1rem;
            }}
            .badge {{
                display: inline-block;
                padding: 0.25rem 0.6rem;
                background: #e0e7ff;
                color: #3730a3;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="status-group">
                <span class="badge">● Cloud Run Active</span>
                {ai_status_badge}
            </div>
            <h1>Zgemini Cloud Hub</h1>
            <p>服務已成功部署至 Google Cloud Run！支援 Google AI Pro 額度串接。</p>
            <ul>
                {links_html}
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
