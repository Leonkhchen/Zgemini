# 🖼️ Windows HEIC 圖片檢視器與轉檔工具 (Viewer & Converter)

這是一套專為 **Windows PC** 設計的本端 HEIC/HEIF 高效看圖與轉檔工具。
無需上傳雲端、無檔案大小限制、注重隱私且完全離線運行！

---

## ✨ 核心特色功能

1. **極速看圖 (HEIC/HEIF Viewer)**：
   - 支援 Apple iPhone / iPad 拍攝的 `.heic` / `.heif` 原始檔案，以及 JPG, PNG, WEBP, BMP 等常見格式。
   - **滑鼠滾輪縮放**：以游標所在位置為中心進行高畫質放大與縮小。
   - **拖曳平移 (Pan)**：放大後按住滑鼠左鍵可任意平移視角。
   - **旋轉校正**：支援順時針/逆時針 90° 旋轉，並自動校正 EXIF 拍攝方向。
   - **EXIF 資訊面板**：即時查看相機型號（如 iPhone 15 Pro）、拍攝時間、光圈、快門、ISO、焦距及解析度。
   - **一鍵複製到剪貼簿 (`Ctrl+C`)**：將目前解碼的高畫質圖片直接複製到 Windows 剪貼簿，可直接 `Ctrl+V` 貼進 LINE、Word、Discord、Photoshop 等。

2. **多功能轉檔 (Converter)**：
   - **單檔即時導出**：可直接將檢視中的圖片另存為 **PNG（無失真）** 或 **JPEG（高品質 1~100% 自由調節）**。
   - **📦 批次轉檔工具 (Batch Converter)**：
     - 一鍵選取多個檔案或整組資料夾。
     - 自由選擇輸出格式（JPEG 或 PNG）、JPEG 壓縮品質（50%~100%）。
     - 支援勾選是否保留原始 EXIF 拍攝時間與相機中繼資料。
     - **多執行緒（Multi-Threading）平行轉檔**，配備即時進度條與轉換狀態回報。

3. **靈活的使用方式**：
   - **檔案拖曳 (Drag & Drop)**：可直接將 HEIC 檔案拖入視窗開啟。
   - **桌面捷徑**：雙擊 `啟動HEIC看圖與轉檔工具.bat` 即可啟動；或將 HEIC 檔案拖放到此 `.bat` 檔圖示上直接開啟。
   - **CLI 命令列模式**：提供 `heic_converter_cli.py`，支援腳本自動化批次處理。

---

## 🚀 快速啟動指南

### 方式一：桌面圖形介面 (GUI)
1. 在檔案總管中直接按兩下執行：
   ```text
   啟動HEIC看圖與轉檔工具.bat
   ```
2. 或在終端機中執行：
   ```bash
   python -m heic_viewer
   ```
   *(亦可指定圖片路徑開啟：`python -m heic_viewer "C:\路徑\相片.heic"`)*

---

## ⌨️ 快捷鍵一覽

| 快捷鍵 | 功能描述 |
| :--- | :--- |
| **`←` / `PageUp`** | 切換至上一張圖片 |
| **`→` / `PageDown`** | 切換至下一張圖片 |
| **`滑鼠滾輪`** | 以游標為中心進行放大 / 縮小 |
| **`滑鼠左鍵拖曳`** | 平移放大後的圖片 |
| **`+` / `-`** | 放大 / 縮小圖片 |
| **`Space` / `0`** | 自動適應視窗大小 (Fit Window) |
| **`1`** | 100% 原始大小比例 (1:1) |
| **`R` / `L`** | 順時針 (R) / 逆時針 (L) 旋轉 90° |
| **`Ctrl + C`** | 複製當前圖片到 Windows 剪貼簿 |
| **`Ctrl + S`** | 另存當前圖片為 JPEG / PNG |
| **`Ctrl + O`** | 開啟單一圖片檔案 |
| **`Ctrl + Shift + O`** | 開啟整組圖片資料夾 |
| **`Ctrl + B`** | 開啟「批次轉檔工具」面板 |
| **`F11`** | 全螢幕檢視切換 |
| **`Esc`** | 退出全螢幕 |

---

## 💻 命令列 (CLI) 轉檔教學

適合進階使用者或批次自動化處理：

### 1. 單一檔案轉換為 JPG
```bash
python heic_converter_cli.py "IMG_0001.HEIC" -o "IMG_0001.jpg" -q 95
```

### 2. 單一檔案轉換為無失真 PNG
```bash
python heic_converter_cli.py "IMG_0001.HEIC" -f png
```

### 3. 整組資料夾批次轉換為 JPG (4 執行緒加速)
```bash
python heic_converter_cli.py "./my_photos" -o "./converted_jpgs" -f jpg -q 92 -w 4
```

### 4. 遞迴搜尋子目錄內所有 HEIC 檔案並轉檔
```bash
python heic_converter_cli.py "./all_trips" -o "./all_jpgs" -r -f jpg
```

### 5. 命令列參數說明
- `path`：來源 HEIC 檔案或資料夾路徑。
- `-o`, `--output`：輸出檔案名稱或儲存資料夾路徑。
- `-f`, `--format`：輸出格式，可選 `jpg` 或 `png` (預設 `jpg`)。
- `-q`, `--quality`：JPEG 壓縮品質 `1~100` (預設 `92`)。
- `-r`, `--recursive`：遞迴搜尋子資料夾內所有 HEIC。
- `-w`, `--workers`：多執行緒並行數 (預設 `4`)。
- `--no-exif`：轉檔時不保留 EXIF 拍攝中繼資料。
- `--view`：直接啟動 GUI 視窗檢視該檔案或資料夾。
