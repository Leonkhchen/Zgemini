import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Zgemini Cloud Run Service")

# Health check endpoint for Cloud Run
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Zgemini Cloud Run Hub"}

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
                max-width: 480px;
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
            }}
            ul {{
                list-style: none;
                padding: 0;
                margin: 0;
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
            .status-badge {{
                display: inline-block;
                padding: 0.25rem 0.6rem;
                background: #dcfce7;
                color: #166534;
                border-radius: 9999px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="status-badge">● Cloud Run Active</span>
            <h1>Zgemini Cloud Hub</h1>
            <p>服務已成功部署至 Google Cloud Run！以下為可存取的專案清單：</p>
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
