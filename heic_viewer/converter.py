# -*- coding: utf-8 -*-
"""
HEIC Converter Engine - 核心轉檔引擎
支援單檔與批次並行多執行緒將 HEIC/HEIF 轉為 PNG / JPEG
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable, Tuple
from PIL import Image, ImageOps
import pillow_heif

# 確保已註冊 heif 開啟器
pillow_heif.register_heif_opener()

def convert_single_image(
    input_path: str,
    output_path: str,
    output_format: str = "JPEG",
    quality: int = 92,
    keep_exif: bool = True
) -> Tuple[bool, str]:
    """
    轉換單一圖片檔案
    :param input_path: 來源圖片路徑 (如 .heic, .png, .jpg)
    :param output_path: 目標輸出路徑
    :param output_format: "JPEG" 或 "PNG"
    :param quality: 輸出品質 (1-100，僅 JPEG 有效)
    :param keep_exif: 是否保留 EXIF 中繼資料
    :return: (是否成功, 訊息)
    """
    output_format = output_format.upper()
    if output_format not in ("JPEG", "JPG", "PNG"):
        return False, f"不支援的輸出格式: {output_format}"

    if output_format == "JPG":
        output_format = "JPEG"

    try:
        # 讀取來源圖片
        with Image.open(input_path) as raw_img:
            # 獲取原始 EXIF
            exif_bytes = None
            if keep_exif:
                exif_bytes = raw_img.info.get("exif")

            # 依 EXIF 方向校正旋轉
            try:
                img = ImageOps.exif_transpose(raw_img)
            except Exception:
                img = raw_img.copy()

            # 確保目標目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            if output_format == "JPEG":
                # JPEG 不支援 RGBA/P 模式，需轉換為 RGB (並將透明背景填為白色)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    alpha_img = img.convert("RGBA")
                    bg = Image.new("RGBA", alpha_img.size, (255, 255, 255, 255))
                    alpha_composite = Image.alpha_composite(bg, alpha_img)
                    save_img = alpha_composite.convert("RGB")
                elif img.mode != "RGB":
                    save_img = img.convert("RGB")
                else:
                    save_img = img

                # 儲存 JPEG
                save_kwargs: Dict[str, Any] = {
                    "format": "JPEG",
                    "quality": max(1, min(100, quality)),
                    "optimize": True
                }
                if exif_bytes and keep_exif:
                    save_kwargs["exif"] = exif_bytes

                save_img.save(output_path, **save_kwargs)

            elif output_format == "PNG":
                # PNG 支援 RGBA 與 RGB，保持高品質
                save_kwargs = {
                    "format": "PNG",
                    "optimize": True
                }
                # PNG 格式儲存
                img.save(output_path, **save_kwargs)

        return True, "轉換成功"
    except Exception as e:
        return False, str(e)


class BatchConvertTask:
    """批次轉檔管理器，支援進度回呼與中途取消"""

    def __init__(
        self,
        file_list: List[str],
        output_dir: str,
        output_format: str = "JPEG",
        quality: int = 92,
        keep_exif: bool = True,
        max_workers: int = 4,
        on_progress: Optional[Callable[[int, int, str, bool, str], None]] = None,
        on_finished: Optional[Callable[[int, int, int], None]] = None
    ):
        """
        :param file_list: 待轉換的檔案完整路徑清單
        :param output_dir: 輸出資料夾路徑
        :param output_format: 'JPEG' 或 'PNG'
        :param quality: JPEG 品質 (1-100)
        :param keep_exif: 是否保留 EXIF
        :param max_workers: 最大執行緒數
        :param on_progress: 進度回呼函數 (已完成數, 總數, 當前檔名, 是否成功, 訊息)
        :param on_finished: 完成回呼函數 (成功數, 失敗數, 總數)
        """
        self.file_list = file_list
        self.output_dir = output_dir
        self.output_format = "JPEG" if output_format.upper() in ("JPEG", "JPG") else "PNG"
        self.quality = quality
        self.keep_exif = keep_exif
        self.max_workers = max_workers
        self.on_progress = on_progress
        self.on_finished = on_finished

        self._cancel_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """非同步啟動批次轉檔執行緒"""
        self._cancel_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        """發送取消信號"""
        self._cancel_event.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        total = len(self.file_list)
        success_count = 0
        failed_count = 0
        completed_count = 0

        target_ext = ".jpg" if self.output_format == "JPEG" else ".png"

        def _worker(filepath: str) -> Tuple[str, bool, str]:
            if self._cancel_event.is_set():
                return filepath, False, "已由使用者取消"
            
            basename = os.path.splitext(os.path.basename(filepath))[0]
            out_filename = f"{basename}{target_ext}"
            out_path = os.path.join(self.output_dir, out_filename)

            # 避免覆寫重名檔案 (如 source 與 output 同資料夾時)
            counter = 1
            while os.path.abspath(out_path) == os.path.abspath(filepath) or (os.path.exists(out_path) and counter > 1):
                out_filename = f"{basename}_{counter}{target_ext}"
                out_path = os.path.join(self.output_dir, out_filename)
                counter += 1

            success, msg = convert_single_image(
                input_path=filepath,
                output_path=out_path,
                output_format=self.output_format,
                quality=self.quality,
                keep_exif=self.keep_exif
            )
            return filepath, success, msg

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(_worker, fp): fp for fp in self.file_list}

            for future in as_completed(future_to_file):
                if self._cancel_event.is_set():
                    break
                
                fp, success, msg = future.result()
                completed_count += 1
                if success:
                    success_count += 1
                else:
                    failed_count += 1

                if self.on_progress:
                    try:
                        self.on_progress(completed_count, total, os.path.basename(fp), success, msg)
                    except Exception:
                        pass

        if self.on_finished:
            try:
                self.on_finished(success_count, failed_count, total)
            except Exception:
                pass
