#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEIC Converter CLI - 命令列轉檔與看圖工具
使用範例：
  1. 轉換單一檔案為 JPG:
     python heic_converter_cli.py photo.heic -o photo.jpg
  2. 轉換單一檔案為 PNG:
     python heic_converter_cli.py photo.heic -f png
  3. 批次轉換整個資料夾所有 HEIC:
     python heic_converter_cli.py ./photos -o ./output_jpg -f jpg -q 95
  4. 啟動 GUI 檢視器看圖:
     python heic_converter_cli.py photo.heic --view
"""

import sys
import os
import argparse
from typing import List

# 確保 Windows 命令列 UTF-8 輸出避免編碼錯誤
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from heic_viewer.converter import convert_single_image, BatchConvertTask
from heic_viewer.utils import is_heic_file, format_file_size

def find_heic_files(target_dir: str, recursive: bool = False) -> List[str]:
    """搜尋指定目錄下的所有 HEIC 檔案"""
    found = []
    if recursive:
        for root, _, files in os.walk(target_dir):
            for file in files:
                if is_heic_file(file):
                    found.append(os.path.join(root, file))
    else:
        for item in os.listdir(target_dir):
            full_path = os.path.join(target_dir, item)
            if os.path.isfile(full_path) and is_heic_file(full_path):
                found.append(full_path)
    return found

def main():
    parser = argparse.ArgumentParser(
        description="HEIC 圖片檢視與格式轉換工具 (支援 PNG & JPEG)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("path", nargs="?", default=".", help="來源 HEIC 檔案或資料夾路徑 (預設為當前目錄)")
    parser.add_argument("-o", "--output", help="輸出檔案或儲存資料夾路徑 (若為資料夾將自動建立)")
    parser.add_argument("-f", "--format", choices=["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"], default="jpg", help="輸出格式 (預設: jpg)")
    parser.add_argument("-q", "--quality", type=int, default=92, help="JPEG 壓縮品質 (1-100，預設: 92)")
    parser.add_argument("-r", "--recursive", action="store_true", help="遞迴搜尋子資料夾內所有 HEIC 檔案")
    parser.add_argument("-w", "--workers", type=int, default=4, help="平行轉檔執行緒數量 (預設: 4)")
    parser.add_argument("--no-exif", action="store_true", help="不保留 EXIF 拍攝資訊 (預設會保留)")
    parser.add_argument("--view", action="store_true", help="直接啟動圖形化視窗檢視器 (GUI Viewer)")

    args = parser.parse_args()

    # 若指定 --view 或是未提供參數直接執行
    if args.view:
        from heic_viewer.app import HEICViewerApp
        app = HEICViewerApp(args.path if args.path != "." else None)
        app.mainloop()
        return

    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"❌ 錯誤：找不到指定的路徑「{target_path}」")
        sys.exit(1)

    output_fmt = "JPEG" if args.format.lower() in ("jpg", "jpeg") else "PNG"
    ext = ".jpg" if output_fmt == "JPEG" else ".png"
    keep_exif = not args.no_exif

    # 情況 A：單一檔案轉換
    if os.path.isfile(target_path):
        if not is_heic_file(target_path):
            print(f"⚠️ 警告：「{target_path}」並非 .heic / .heif 格式，仍嘗試轉換...")

        if args.output:
            if os.path.isdir(args.output):
                base = os.path.splitext(os.path.basename(target_path))[0]
                out_file = os.path.join(args.output, f"{base}{ext}")
            else:
                out_file = args.output
        else:
            base = os.path.splitext(target_path)[0]
            out_file = f"{base}{ext}"

        print(f"🔄 正在轉換：{os.path.basename(target_path)} -> {os.path.basename(out_file)} (格式: {output_fmt}, 品質: {args.quality})")
        ok, msg = convert_single_image(
            input_path=target_path,
            output_path=out_file,
            output_format=output_fmt,
            quality=args.quality,
            keep_exif=keep_exif
        )
        if ok:
            sz = format_file_size(os.path.getsize(out_file))
            print(f"✅ 轉換成功！輸出檔案大小：{sz}\n路徑：{out_file}")
        else:
            print(f"❌ 轉換失敗：{msg}")
            sys.exit(1)
        return

    # 情況 B：資料夾批次轉換
    if os.path.isdir(target_path):
        heic_files = find_heic_files(target_path, recursive=args.recursive)
        if not heic_files:
            print(f"ℹ️ 資料夾「{target_path}」內未找到任何 .heic / .heif 檔案。")
            return

        out_dir = os.path.abspath(args.output) if args.output else target_path
        os.makedirs(out_dir, exist_ok=True)

        print(f"📦 找到 {len(heic_files)} 個 HEIC 檔案，開始批次轉換至「{out_dir}」...")
        print(f"⚙️ 設定：格式={output_fmt}, 品質={args.quality}, 執行緒={args.workers}, 保留EXIF={keep_exif}\n")

        def on_prog(done, total, fname, success, msg):
            status = "✅ 成功" if success else f"❌ 失敗: {msg}"
            pct = int((done / total) * 100)
            print(f"[{done}/{total} {pct:>3}%] {fname} -> {status}")

        def on_done(success_cnt, fail_cnt, total):
            print("\n" + "="*50)
            print(f"🎉 批次轉檔完成！總共 {total} 個，成功: {success_cnt} 個，失敗: {fail_cnt} 個。")
            print(f"📂 輸出儲存目錄：{out_dir}")
            print("="*50)

        task = BatchConvertTask(
            file_list=heic_files,
            output_dir=out_dir,
            output_format=output_fmt,
            quality=args.quality,
            keep_exif=keep_exif,
            max_workers=args.workers,
            on_progress=on_prog,
            on_finished=on_done
        )
        task._run()  # CLI 直接同步執行

if __name__ == "__main__":
    main()
