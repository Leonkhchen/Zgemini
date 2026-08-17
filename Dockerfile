# 使用官方輕量 Python 3.11 映象檔
FROM python:3.11-slim

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 設定工作目錄
WORKDIR /app

# 先複製依賴設定以利用 Docker 快取層
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案原始碼
COPY . .

# 暴露預設連接埠 (Cloud Run 運行時會自動注入 $PORT)
EXPOSE 8080

# 啟動應用程式 (綁定 0.0.0.0 並讀取 $PORT)
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
