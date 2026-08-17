# -*- coding: utf-8 -*-
"""
HEIC Viewer & Converter - Windows 本端主程式
提供 HEIC 圖片檢視、流暢縮放、旋轉、單檔/批次轉檔為 PNG & JPEG
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional
from PIL import Image

# 匯入內部模組
from .utils import (
    load_image_with_exif, get_image_metadata, scan_directory_images,
    is_heic_file, is_supported_image, copy_image_to_windows_clipboard
)
from .converter import convert_single_image
from .ui_components import ImageViewerCanvas, BatchConvertDialog

# 支援拖曳支援 (TkinterDnD2)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

BaseWindow = TkinterDnD.Tk if HAS_DND else tk.Tk

class HEICViewerApp(BaseWindow):
    """HEIC 圖片檢視器與轉檔工具主視窗"""

    def __init__(self, initial_path: Optional[str] = None):
        super().__init__()
        self.title("HEIC 圖片檢視器 & 轉檔工具 (Windows PC)")
        self.geometry("1180x760")
        self.minsize(800, 500)
        self.configure(bg="#1e1e1e")

        # 狀態變數
        self.current_folder: Optional[str] = None
        self.file_list: List[str] = []
        self.current_index: int = -1
        self.current_pil_image: Optional[Image.Image] = None
        self.current_exif: dict = {}
        self.is_fullscreen: bool = False

        # 初始化 UI 與樣式 (先建立 main_content 以產生 canvas)
        self._init_style()
        self._create_toolbar()
        self._create_main_content()
        self._create_menu()
        self._create_statusbar()
        self._bind_shortcuts()
        self._setup_drag_and_drop()

        # 若啟動時有指定檔案
        if initial_path and os.path.exists(initial_path):
            self.load_path(initial_path)

    def _init_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # 深色主題樣式設定
        self.style.configure(".", background="#2b2b2b", foreground="#ffffff", font=("Segoe UI", 9))
        self.style.configure("Treeview", background="#232323", foreground="#ffffff", fieldbackground="#232323", rowheight=26)
        self.style.map("Treeview", background=[("selected", "#094771")], foreground=[("selected", "#ffffff")])
        self.style.configure("TProgressbar", thickness=14, troughcolor="#1e1e1e", background="#4caf50")
        self.style.configure("Vertical.TScrollbar", troughcolor="#232323", background="#3c3f41", arrowcolor="#ffffff")

    def _create_menu(self):
        menubar = tk.Menu(self, bg="#2b2b2b", fg="#ffffff", activebackground="#094771", activeforeground="#ffffff")

        # 檔案選單
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#094771", activeforeground="#ffffff")
        file_menu.add_command(label="開啟檔案... (Ctrl+O)", command=self.open_file_dialog)
        file_menu.add_command(label="開啟資料夾... (Ctrl+Shift+O)", command=self.open_folder_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="另存為 PNG... (無失真)", command=lambda: self.save_current_as("PNG"))
        file_menu.add_command(label="另存為 JPEG... (高品質)", command=lambda: self.save_current_as("JPEG"))
        file_menu.add_separator()
        file_menu.add_command(label="📦 批次轉檔工具... (Ctrl+B)", command=self.open_batch_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="離開 (Alt+F4)", command=self.quit)
        menubar.add_cascade(label="檔案 (F)", menu=file_menu)

        # 檢視選單
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#094771", activeforeground="#ffffff")
        view_menu.add_command(label="上一張圖片 (← / PageUp)", command=self.prev_image)
        view_menu.add_command(label="下一張圖片 (→ / PageDown)", command=self.next_image)
        view_menu.add_separator()
        view_menu.add_command(label="放大 (Ctrl + / 滾輪向上)", command=lambda: self.canvas.zoom_in())
        view_menu.add_command(label="縮小 (Ctrl - / 滾輪向下)", command=lambda: self.canvas.zoom_out())
        view_menu.add_command(label="適應視窗大小 (Space / 0)", command=lambda: self.canvas.fit_to_window())
        view_menu.add_command(label="100% 原始大小 (1)", command=lambda: self.canvas.zoom_actual())
        view_menu.add_separator()
        view_menu.add_command(label="順時針旋轉 90° (R)", command=lambda: self.canvas.rotate_cw())
        view_menu.add_command(label="逆時針旋轉 90° (L)", command=lambda: self.canvas.rotate_ccw())
        view_menu.add_separator()
        view_menu.add_command(label="全螢幕切換 (F11)", command=self.toggle_fullscreen)
        menubar.add_cascade(label="檢視 (V)", menu=view_menu)

        # 工具選單
        tool_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#094771", activeforeground="#ffffff")
        tool_menu.add_command(label="複製圖片到剪貼簿 (Ctrl+C)", command=self.copy_to_clipboard)
        tool_menu.add_command(label="📦 批次轉檔全部目前資料夾", command=self.batch_convert_current_folder)
        menubar.add_cascade(label="工具 (T)", menu=tool_menu)

        # 說明選單
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="#ffffff", activebackground="#094771", activeforeground="#ffffff")
        help_menu.add_command(label="使用說明與快捷鍵", command=self.show_help)
        help_menu.add_command(label="關於本軟體", command=self.show_about)
        menubar.add_cascade(label="說明 (H)", menu=help_menu)

        self.config(menu=menubar)

    def _create_toolbar(self):
        toolbar = tk.Frame(self, bg="#2d2d2d", height=42, padx=8, pady=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        def make_btn(parent, text, cmd, bg="#3c3f41", fg="#ffffff", font_size=9, pad=6):
            btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, relief=tk.FLAT, font=("Segoe UI", font_size), padx=pad, pady=3, activebackground="#505357", activeforeground="#ffffff", cursor="hand2")
            btn.pack(side=tk.LEFT, padx=3)
            return btn

        # 檔案操作按鈕
        make_btn(toolbar, "📂 開啟檔案", self.open_file_dialog)
        make_btn(toolbar, "📁 開啟資料夾", self.open_folder_dialog)

        # 分隔線
        tk.Frame(toolbar, width=2, bg="#444444").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        # 導覽按鈕
        self.prev_btn = make_btn(toolbar, "◀ 上一張", self.prev_image)
        self.next_btn = make_btn(toolbar, "下一張 ▶", self.next_image)
        self.index_label = tk.Label(toolbar, text="0 / 0", bg="#2d2d2d", fg="#bbbbbb", font=("Segoe UI", 9, "bold"), padx=6)
        self.index_label.pack(side=tk.LEFT)

        # 分隔線
        tk.Frame(toolbar, width=2, bg="#444444").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        # 縮放與檢視
        make_btn(toolbar, "🔍+", self.canvas_zoom_in, pad=4)
        make_btn(toolbar, "🔍-", self.canvas_zoom_out, pad=4)
        make_btn(toolbar, "🔲 視窗適應", self.canvas_fit)
        make_btn(toolbar, "1:1", self.canvas_actual, pad=4)
        make_btn(toolbar, "↺ 旋轉", self.canvas_rotate_ccw, pad=4)
        make_btn(toolbar, "↻ 旋轉", self.canvas_rotate_cw, pad=4)

        # 分隔線
        tk.Frame(toolbar, width=2, bg="#444444").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        # 轉檔與剪貼簿
        make_btn(toolbar, "💾 另存 PNG", lambda: self.save_current_as("PNG"), bg="#1e6b37")
        make_btn(toolbar, "💾 另存 JPEG", lambda: self.save_current_as("JPEG"), bg="#1e6b37")
        make_btn(toolbar, "📋 複製圖片", self.copy_to_clipboard, bg="#2a5f8a")

        # 批次轉檔特別高亮
        batch_btn = tk.Button(toolbar, text="📦 批次轉檔工具", command=self.open_batch_dialog, bg="#b35900", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=3, activebackground="#cc6600", activeforeground="#ffffff", cursor="hand2")
        batch_btn.pack(side=tk.RIGHT, padx=4)

        # 側邊欄切換
        self.toggle_side_btn = tk.Button(toolbar, text="📑 檔案清單", command=self.toggle_sidebar, bg="#3c3f41", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=6, pady=3, cursor="hand2")
        self.toggle_side_btn.pack(side=tk.RIGHT, padx=4)

    def _create_main_content(self):
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e1e", sashrelief=tk.FLAT, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 左側檔案清單面板
        self.sidebar_frame = tk.Frame(self.paned, bg="#232323", width=260)
        self.sidebar_frame.pack_propagate(False)

        # 側邊欄標題
        side_header = tk.Frame(self.sidebar_frame, bg="#282828", padx=8, pady=6)
        side_header.pack(fill=tk.X)
        tk.Label(side_header, text="📁 資料夾檔案清單", bg="#282828", fg="#ffffff", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        # 檔案清單 Treeview
        tree_scroll = ttk.Scrollbar(self.sidebar_frame, orient=tk.VERTICAL)
        self.file_tree = ttk.Treeview(self.sidebar_frame, columns=("name", "size"), show="headings", selectmode="browse", yscrollcommand=tree_scroll.set)
        self.file_tree.heading("name", text="名稱")
        self.file_tree.heading("size", text="大小")
        self.file_tree.column("name", width=170)
        self.file_tree.column("size", width=70, anchor=tk.E)
        
        tree_scroll.config(command=self.file_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # 圖片詳細 EXIF 資訊區 (側邊欄底部)
        self.exif_frame = tk.LabelFrame(self.sidebar_frame, text=" 圖片詳細資訊 ", bg="#232323", fg="#bbbbbb", font=("Segoe UI", 8, "bold"), padx=6, pady=6)
        self.exif_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=4)
        
        self.info_labels = {}
        for key in ["解析度", "檔案大小", "色彩模式", "相機/裝置", "拍攝時間", "拍攝參數"]:
            row = tk.Frame(self.exif_frame, bg="#232323")
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{key}:", bg="#232323", fg="#888888", font=("Segoe UI", 8), width=7, anchor=tk.W).pack(side=tk.LEFT)
            lbl = tk.Label(row, text="-", bg="#232323", fg="#dddddd", font=("Segoe UI", 8), anchor=tk.W, wraplength=180, justify=tk.LEFT)
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.info_labels[key] = lbl

        # 右側主檢視畫布
        self.canvas = ImageViewerCanvas(self.paned, bg_color="#181818")

        self.paned.add(self.sidebar_frame, minsize=180)
        self.paned.add(self.canvas, minsize=400)
        self.paned.paneconfig(self.sidebar_frame, width=260)

    def _create_statusbar(self):
        self.statusbar = tk.Frame(self, bg="#252525", height=24, padx=8, pady=2)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_file_lbl = tk.Label(self.statusbar, text="就緒 (支援將 .HEIC 檔案直接拖曳進來檢視)", bg="#252525", fg="#aaaaaa", font=("Segoe UI", 9), anchor=tk.W)
        self.status_file_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_zoom_lbl = tk.Label(self.statusbar, text="", bg="#252525", fg="#4caf50", font=("Segoe UI", 9), anchor=tk.E)
        self.status_zoom_lbl.pack(side=tk.RIGHT, padx=6)

    def _bind_shortcuts(self):
        self.bind("<Left>", lambda e: self.prev_image())
        self.bind("<Right>", lambda e: self.next_image())
        self.bind("<Prior>", lambda e: self.prev_image())  # PageUp
        self.bind("<Next>", lambda e: self.next_image())   # PageDown
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<Control-O>", lambda e: self.open_file_dialog())
        self.bind("<Control-Shift-O>", lambda e: self.open_folder_dialog())
        self.bind("<Control-Shift-o>", lambda e: self.open_folder_dialog())
        self.bind("<Control-s>", lambda e: self.save_current_as("JPEG"))
        self.bind("<Control-S>", lambda e: self.save_current_as("JPEG"))
        self.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.bind("<Control-C>", lambda e: self.copy_to_clipboard())
        self.bind("<Control-b>", lambda e: self.open_batch_dialog())
        self.bind("<Control-B>", lambda e: self.open_batch_dialog())
        self.bind("<space>", lambda e: self.canvas.fit_to_window())
        self.bind("0", lambda e: self.canvas.fit_to_window())
        self.bind("1", lambda e: self.canvas.zoom_actual())
        self.bind("<plus>", lambda e: self.canvas.zoom_in())
        self.bind("<equal>", lambda e: self.canvas.zoom_in())
        self.bind("<minus>", lambda e: self.canvas.zoom_out())
        self.bind("r", lambda e: self.canvas.rotate_cw())
        self.bind("R", lambda e: self.canvas.rotate_cw())
        self.bind("l", lambda e: self.canvas.rotate_ccw())
        self.bind("L", lambda e: self.canvas.rotate_ccw())
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _setup_drag_and_drop(self):
        if HAS_DND:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop_files)

    def _on_drop_files(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            first_path = files[0].strip('{}')
            if os.path.exists(first_path):
                self.load_path(first_path)

    # 畫布代理方法
    def canvas_zoom_in(self):
        self.canvas.zoom_in()

    def canvas_zoom_out(self):
        self.canvas.zoom_out()

    def canvas_fit(self):
        self.canvas.fit_to_window()

    def canvas_actual(self):
        self.canvas.zoom_actual()

    def canvas_rotate_cw(self):
        self.canvas.rotate_cw()

    def canvas_rotate_ccw(self):
        self.canvas.rotate_ccw()

    def toggle_sidebar(self):
        """展開或收合左側清單"""
        panes = self.paned.panes()
        if str(self.sidebar_frame) in panes:
            self.paned.remove(self.sidebar_frame)
            self.toggle_side_btn.configure(bg="#2b2b2b", text="📑 顯示清單")
        else:
            self.paned.insert(0, self.sidebar_frame, minsize=180, width=260)
            self.toggle_side_btn.configure(bg="#3c3f41", text="📑 隱藏清單")

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def _exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.attributes("-fullscreen", False)

    def open_file_dialog(self):
        path = filedialog.askopenfilename(
            title="選擇圖片檔案",
            filetypes=[
                ("HEIC / 圖片格式", "*.heic;*.heif;*.jpg;*.jpeg;*.png;*.webp;*.bmp"),
                ("HEIC / HEIF 檔案", "*.heic;*.heif"),
                ("所有檔案", "*.*")
            ]
        )
        if path:
            self.load_path(path)

    def open_folder_dialog(self):
        folder = filedialog.askdirectory(title="選擇包含 HEIC 圖片的資料夾")
        if folder:
            self.load_folder(folder)

    def load_path(self, path: str):
        """載入指定檔案或資料夾路徑"""
        if os.path.isdir(path):
            self.load_folder(path)
        elif os.path.isfile(path):
            folder = os.path.dirname(path)
            self.load_folder(folder, target_file=path)

    def load_folder(self, folder: str, target_file: Optional[str] = None):
        """載入資料夾內所有圖片"""
        self.current_folder = folder
        self.file_list = scan_directory_images(folder)

        # 更新側邊欄清單
        self.file_tree.delete(*self.file_tree.get_children())
        target_item_id = None

        for idx, f in enumerate(self.file_list):
            try:
                sz = format_file_size(os.path.getsize(f))
            except Exception:
                sz = "-"
            item_id = self.file_tree.insert("", tk.END, iid=str(idx), values=(os.path.basename(f), sz))
            if target_file and os.path.abspath(f) == os.path.abspath(target_file):
                target_item_id = item_id

        if not self.file_list:
            self.current_index = -1
            self.canvas.clear()
            self.index_label.configure(text="0 / 0")
            self.status_file_lbl.configure(text=f"資料夾「{os.path.basename(folder)}」內無支援的圖片格式")
            return

        if target_item_id is not None:
            self.current_index = int(target_item_id)
        else:
            self.current_index = 0

        self._show_image_at_index(self.current_index)

    def _on_tree_select(self, event):
        selected = self.file_tree.selection()
        if selected:
            idx = int(selected[0])
            if idx != self.current_index:
                self.current_index = idx
                self._show_image_at_index(self.current_index, sync_tree=False)

    def _show_image_at_index(self, index: int, sync_tree: bool = True):
        if not (0 <= index < len(self.file_list)):
            return

        filepath = self.file_list[index]
        self.current_index = index
        self.index_label.configure(text=f"{index + 1} / {len(self.file_list)}")

        if sync_tree:
            self.file_tree.selection_set(str(index))
            self.file_tree.see(str(index))

        # 讀取並渲染圖片
        try:
            img, exif = load_image_with_exif(filepath)
            self.current_pil_image = img
            self.current_exif = exif
            self.canvas.load_image(img, auto_fit=True)

            # 更新中繼資訊
            meta = get_image_metadata(filepath, img, exif)
            for k, lbl in self.info_labels.items():
                lbl.configure(text=meta.get(k, "-"))

            filename = os.path.basename(filepath)
            self.title(f"{filename} ({img.width}×{img.height}) - HEIC 圖片檢視器")
            self.status_file_lbl.configure(text=f"📂 {filepath}")
        except Exception as e:
            self.canvas.clear()
            messagebox.showerror("載入錯誤", str(e), parent=self)

    def prev_image(self):
        if not self.file_list:
            return
        new_idx = (self.current_index - 1) % len(self.file_list)
        self._show_image_at_index(new_idx)

    def next_image(self):
        if not self.file_list:
            return
        new_idx = (self.current_index + 1) % len(self.file_list)
        self._show_image_at_index(new_idx)

    def save_current_as(self, default_format: str = "JPEG"):
        """另存當前檢視的圖片為 PNG 或 JPEG"""
        if not self.file_list or self.current_index < 0:
            messagebox.showinfo("提示", "請先開啟一張圖片！", parent=self)
            return

        src_path = self.file_list[self.current_index]
        base = os.path.splitext(os.path.basename(src_path))[0]

        ext = ".jpg" if default_format.upper() in ("JPEG", "JPG") else ".png"
        file_types = [("JPEG 圖片 (*.jpg)", "*.jpg")] if default_format.upper() in ("JPEG", "JPG") else [("PNG 圖片 (*.png)", "*.png")]

        out_path = filedialog.asksaveasfilename(
            title=f"另存為 {default_format}",
            initialdir=os.path.dirname(src_path),
            initialfile=f"{base}{ext}",
            filetypes=file_types + [("所有檔案", "*.*")]
        )

        if out_path:
            # 依附檔名判斷格式
            out_ext = os.path.splitext(out_path)[1].lower()
            save_format = "PNG" if out_ext == ".png" else "JPEG"

            success, msg = convert_single_image(
                input_path=src_path,
                output_path=out_path,
                output_format=save_format,
                quality=95,
                keep_exif=True
            )
            if success:
                messagebox.showinfo("儲存成功", f"檔案已成功儲存至：\n{out_path}", parent=self)
            else:
                messagebox.showerror("儲存失敗", f"轉檔儲存失敗：{msg}", parent=self)

    def copy_to_clipboard(self):
        """複製當前旋轉顯示的圖片到 Windows 剪貼簿"""
        cur_img = self.canvas.get_current_image()
        if cur_img is None:
            messagebox.showinfo("提示", "目前沒有已載入的圖片可供複製！", parent=self)
            return

        ok = copy_image_to_windows_clipboard(cur_img)
        if ok:
            # 短暫在狀態列提示
            self.status_file_lbl.configure(text="✅ 圖片已成功複製至 Windows 剪貼簿！可直接貼到 LINE / Word / 軟體中")
        else:
            messagebox.showwarning("複製失敗", "無法將圖片寫入 Windows 剪貼簿", parent=self)

    def open_batch_dialog(self):
        """開啟批次轉檔視窗"""
        default_files = self.file_list if self.file_list else []
        default_dir = self.current_folder if self.current_folder else ""
        BatchConvertDialog(self, default_files=default_files, default_dir=default_dir)

    def batch_convert_current_folder(self):
        if not self.file_list:
            messagebox.showinfo("提示", "目前資料夾沒有圖片項目可轉檔！", parent=self)
            return
        self.open_batch_dialog()

    def show_help(self):
        help_text = (
            "【HEIC 看圖與轉檔工具 快捷鍵一覽】\n\n"
            "• 導覽切換：\n"
            "   ← / PageUp ：上一張圖片\n"
            "   → / PageDown：下一張圖片\n\n"
            "• 畫面縮放與旋轉：\n"
            "   滑鼠滾輪    ：以游標位置為中心放大/縮小\n"
            "   滑鼠左鍵拖曳：平移放大後的圖片\n"
            "   + / -       ：放大 / 縮小\n"
            "   Space / 0   ：適應視窗大小 (Fit Window)\n"
            "   1           ：100% 原始比例 (1:1)\n"
            "   R / L       ：順時針 / 逆時針旋轉 90°\n"
            "   F11         ：切換全螢幕\n\n"
            "• 檔案與轉檔：\n"
            "   Ctrl + O    ：開啟檔案\n"
            "   Ctrl + Shift + O ：開啟資料夾\n"
            "   Ctrl + S    ：另存為 JPEG\n"
            "   Ctrl + C    ：複製圖片到 Windows 剪貼簿\n"
            "   Ctrl + B    ：開啟批次轉檔工具\n"
            "   支援將 HEIC 檔案直接拖曳進視窗！"
        )
        messagebox.showinfo("使用說明與快捷鍵", help_text, parent=self)

    def show_about(self):
        about_text = (
            "HEIC 圖片檢視器 & 轉檔工具 (Windows PC 版)\n\n"
            "版本：1.0.0\n"
            "支援格式：Apple HEIC / HEIF, JPG, PNG, WEBP, BMP 等\n"
            "核心：Pillow + libheif (pillow-heif)\n"
            "特點：純本端離線處理、無雲端上傳、多執行緒極速轉檔。"
        )
        messagebox.showinfo("關於", about_text, parent=self)


def main():
    initial_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = HEICViewerApp(initial_path)
    app.mainloop()

if __name__ == "__main__":
    main()
