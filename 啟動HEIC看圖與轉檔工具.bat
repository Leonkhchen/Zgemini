@echo off
chcp 65001 >nul
title HEIC 圖片檢視器與轉檔工具

:: 切換至腳本所在目錄
cd /d "%~dp0"

echo 正在啟動 HEIC 看圖與轉檔程式...

:: 檢查 python 是否存在
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python 環境，請確認已安裝 Python 3 並加入 PATH 環境變數。
    pause
    exit /b 1
)

:: 啟動程式 (支援將 HEIC 檔案直接拖拉到此 .bat 檔圖示上開啟)
if "%~1"=="" (
    start "" pythonw -m heic_viewer
) else (
    start "" pythonw -m heic_viewer "%~1"
)

exit
