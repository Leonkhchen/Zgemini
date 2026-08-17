# -*- coding: utf-8 -*-
"""
HEIC Viewer & Converter - 工具模組
包含 HEIC 解碼、EXIF 解析、剪貼簿操作及檔案處理
"""

import io
import os
import ctypes
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageOps, ExifTags
import pillow_heif

# 註冊 pillow_heif 開啟 HEIC / HEIF 支援
pillow_heif.register_heif_opener()

SUPPORTED_HEIC_EXTENSIONS = {'.heic', '.heif'}
SUPPORTED_IMAGE_EXTENSIONS = {
    '.heic', '.heif', '.jpg', '.jpeg', '.png',
    '.webp', '.bmp', '.gif', '.tiff', '.tif'
}

def is_heic_file(filepath: str) -> bool:
    """判斷檔案是否為 HEIC / HEIF 格式"""
    _, ext = os.path.splitext(filepath.lower())
    return ext in SUPPORTED_HEIC_EXTENSIONS

def is_supported_image(filepath: str) -> bool:
    """判斷檔案是否為支援的圖片格式"""
    _, ext = os.path.splitext(filepath.lower())
    return ext in SUPPORTED_IMAGE_EXTENSIONS

def load_image_with_exif(filepath: str) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    載入圖片並進行 EXIF 自動旋轉，回傳 (PIL.Image, EXIF 資訊字典)
    """
    try:
        raw_img = Image.open(filepath)
        
        # 讀取 EXIF 資訊
        exif_data = {}
        raw_exif = raw_img.getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                exif_data[tag_name] = value

        # 自動修正 EXIF 拍攝方向 (Orientation)
        try:
            img = ImageOps.exif_transpose(raw_img)
        except Exception:
            img = raw_img

        # 確保在記憶體中保留可用影像 (特別是 HEIC 需要載入像素)
        img.load()
        return img, exif_data
    except Exception as e:
        raise RuntimeError(f"載入圖片失敗 '{os.path.basename(filepath)}': {str(e)}")

def format_file_size(size_bytes: int) -> str:
    """格式化檔案大小 (KB, MB)"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def get_image_metadata(filepath: str, img: Optional[Image.Image] = None, exif_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """獲取圖片結構化中繼資料供 UI 顯示"""
    metadata = {}
    try:
        stat = os.stat(filepath)
        metadata["檔案名稱"] = os.path.basename(filepath)
        metadata["檔案大小"] = format_file_size(stat.st_size)
        metadata["檔案路徑"] = filepath
    except Exception:
        metadata["檔案名稱"] = os.path.basename(filepath)

    if img is not None:
        metadata["解析度"] = f"{img.width} × {img.height} 像素"
        metadata["色彩模式"] = img.mode
        metadata["格式"] = img.format if img.format else os.path.splitext(filepath)[1].upper().replace('.', '')

    if exif_data:
        # 相機製造商與型號
        make = exif_data.get("Make", "").strip()
        model = exif_data.get("Model", "").strip()
        if make or model:
            metadata["相機/裝置"] = f"{make} {model}".strip()

        # 拍攝時間
        dt = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
        if dt:
            metadata["拍攝時間"] = str(dt)

        # 鏡頭光圈與曝光
        f_number = exif_data.get("FNumber")
        exposure_time = exif_data.get("ExposureTime")
        iso = exif_data.get("ISOSpeedRatings") or exif_data.get("PhotographicSensitivity")
        focal_length = exif_data.get("FocalLength")

        exp_details = []
        if f_number:
            exp_details.append(f"f/{float(f_number):.1f}")
        if exposure_time:
            exp_details.append(f"{exposure_time}s" if isinstance(exposure_time, str) else f"1/{round(1/float(exposure_time))}s" if float(exposure_time) < 1 else f"{exposure_time}s")
        if iso:
            exp_details.append(f"ISO {iso}")
        if focal_length:
            exp_details.append(f"{float(focal_length):.1f}mm")
        
        if exp_details:
            metadata["拍攝參數"] = " | ".join(exp_details)

        # 軟體
        software = exif_data.get("Software")
        if software:
            metadata["軟體"] = str(software)

    return metadata

def scan_directory_images(directory: str) -> List[str]:
    """掃描指定資料夾中的所有圖片檔案（包含 HEIC/HEIF），並按自然名稱排序"""
    if not os.path.isdir(directory):
        return []
    
    files = []
    try:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path) and is_supported_image(full_path):
                files.append(full_path)
    except Exception:
        pass

    # 自然排序 (Natural sort)
    import re
    def natural_keys(text):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

    files.sort(key=natural_keys)
    return files

def copy_image_to_windows_clipboard(img: Image.Image) -> bool:
    """
    將 PIL Image 轉換為 DIB 格式並複製到 Windows 剪貼簿
    """
    try:
        output = io.BytesIO()
        # 轉換為 RGB 格式（DIB 點陣圖標準）
        rgb_img = img.convert("RGB")
        rgb_img.save(output, format="BMP")
        data = output.getvalue()[14:]  # 去掉 14 位元組的 BMP Header，保留 DIB (BITMAPINFOHEADER + 點陣資料)
        output.close()

        # Windows API 操作剪貼簿
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        CF_DIB = 8
        GMEM_MOVEABLE = 0x0002

        if not user32.OpenClipboard(0):
            return False

        user32.EmptyClipboard()
        h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h_global:
            user32.CloseClipboard()
            return False

        p_global = kernel32.GlobalLock(h_global)
        ctypes.memmove(p_global, data, len(data))
        kernel32.GlobalUnlock(h_global)

        user32.SetClipboardData(CF_DIB, h_global)
        user32.CloseClipboard()
        return True
    except Exception as e:
        print(f"複製到剪貼簿錯誤: {e}")
        return False
