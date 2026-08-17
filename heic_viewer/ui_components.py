# -*- coding: utf-8 -*-
"""
HEIC Viewer & Converter - UI 介面自訂元件
包含圖片縮放平移畫布 (ImageViewerCanvas) 與批次轉檔對話框 (BatchConvertDialog)
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Callable
from PIL import Image, ImageTk, ImageOps

from .converter import BatchConvertTask
from .utils import scan_directory_images, is_heic_file, format_file_size

class ImageViewerCanvas(tk.Canvas):
    """
    高效能圖片檢視畫布
    支援：滾輪以游標為中心縮放、滑鼠拖曳平移、90度旋轉、適應視窗與 100% 原始大小
    """

    def __init__(self, master, bg_color="#1e1e1e", **kwargs):
        super().__init__(master, bg=bg_color, highlightthickness=0, **kwargs)
        
        self.raw_image: Optional[Image.Image] = None
        self.display_image: Optional[Image.Image] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.image_id: Optional[int] = None

        # 狀態控制
        self.scale: float = 1.0
        self.min_scale: float = 0.05
        self.max_scale: float = 20.0
        self.rotation: int = 0  # 0, 90, 180, 270
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        
        # 滑鼠拖曳記憶
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False

        # 綁定事件
        self.bind("<Configure>", self._on_resize)
        self.bind("<ButtonPress-1>", self._on_button_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_button_release)
        self.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows 滾輪
        self.bind("<Double-Button-1>", lambda e: self.fit_to_window())

        # 提示文字
        self._empty_text_id = self.create_text(
            0, 0,
            text="尚未載入圖片\n請點擊「開啟檔案」或將 HEIC 圖片拖曳至此",
            fill="#888888",
            font=("Segoe UI", 14),
            justify=tk.CENTER
        )

    def load_image(self, pil_image: Image.Image, auto_fit: bool = True):
        """載入新的 PIL 圖片並重設檢視狀態"""
        self.raw_image = pil_image
        self.rotation = 0
        self._update_display_image()
        
        if auto_fit:
            self.fit_to_window()
        else:
            self.redraw()

    def clear(self):
        """清除當前畫面"""
        self.raw_image = None
        self.display_image = None
        self.photo_image = None
        if self.image_id:
            self.delete(self.image_id)
            self.image_id = None
        self.itemconfig(self._empty_text_id, state="normal")
        self._center_empty_text()

    def rotate_cw(self):
        """順時針旋轉 90 度"""
        if not self.raw_image:
            return
        self.rotation = (self.rotation - 90) % 360  # PIL rotate 方向為逆時針，因此 -90
        self._update_display_image()
        self.fit_to_window()

    def rotate_ccw(self):
        """逆時針旋轉 90 度"""
        if not self.raw_image:
            return
        self.rotation = (self.rotation + 90) % 360
        self._update_display_image()
        self.fit_to_window()

    def zoom_in(self, factor: float = 1.25):
        """放大"""
        if not self.display_image:
            return
        cw, ch = self.winfo_width(), self.winfo_height()
        self._zoom_at(cw / 2, ch / 2, factor)

    def zoom_out(self, factor: float = 0.8):
        """縮小"""
        if not self.display_image:
            return
        cw, ch = self.winfo_width(), self.winfo_height()
        self._zoom_at(cw / 2, ch / 2, factor)

    def fit_to_window(self):
        """自動縮放並居中以適應目前視窗大小"""
        if not self.display_image:
            return
        
        cw = max(10, self.winfo_width())
        ch = max(10, self.winfo_height())
        iw, ih = self.display_image.size

        # 留 20px 邊距
        scale_w = (cw - 40) / iw
        scale_h = (ch - 40) / ih
        self.scale = max(self.min_scale, min(scale_w, scale_h, 1.0))
        
        # 居中顯示
        self.offset_x = (cw - iw * self.scale) / 2
        self.offset_y = (ch - ih * self.scale) / 2
        self.redraw()

    def zoom_actual(self):
        """以 100% 原始比例顯示 (1:1)"""
        if not self.display_image:
            return
        cw = self.winfo_width()
        ch = self.winfo_height()
        iw, ih = self.display_image.size
        
        self.scale = 1.0
        self.offset_x = (cw - iw) / 2
        self.offset_y = (ch - ih) / 2
        self.redraw()

    def get_current_image(self) -> Optional[Image.Image]:
        """獲取當前旋轉後的 PIL 圖片"""
        return self.display_image

    def _update_display_image(self):
        if not self.raw_image:
            self.display_image = None
            return
        if self.rotation != 0:
            self.display_image = self.raw_image.rotate(self.rotation, expand=True)
        else:
            self.display_image = self.raw_image.copy()

    def redraw(self):
        """根據當前 scale 與 offset 重新繪製圖片"""
        if not self.display_image:
            self.clear()
            return

        self.itemconfig(self._empty_text_id, state="hidden")

        # 計算顯示寬高
        iw, ih = self.display_image.size
        target_w = max(1, int(iw * self.scale))
        target_h = max(1, int(ih * self.scale))

        # 高品質重採樣
        try:
            # 放大時使用 Bilinear / Nearest 加速，縮小時使用 Box / Lanczos
            resample = Image.Resampling.LANCZOS if self.scale < 1.0 else Image.Resampling.BILINEAR
            resized = self.display_image.resize((target_w, target_h), resample)
            self.photo_image = ImageTk.PhotoImage(resized)

            if self.image_id is None:
                self.image_id = self.create_image(
                    self.offset_x, self.offset_y,
                    image=self.photo_image,
                    anchor=tk.NW
                )
            else:
                self.coords(self.image_id, self.offset_x, self.offset_y)
                self.itemconfig(self.image_id, image=self.photo_image)
        except Exception as e:
            print(f"Redraw error: {e}")

    def _zoom_at(self, mouse_x: float, mouse_y: float, factor: float):
        """以指定座標為中心點進行縮放"""
        if not self.display_image:
            return
        
        old_scale = self.scale
        new_scale = max(self.min_scale, min(self.max_scale, old_scale * factor))
        if new_scale == old_scale:
            return

        # 保持滑鼠指向之圖片相對位置不變
        # image_x = (mouse_x - offset_x) / old_scale
        # mouse_x = offset_x_new + image_x * new_scale
        # => offset_x_new = mouse_x - (mouse_x - offset_x) * (new_scale / old_scale)
        ratio = new_scale / old_scale
        self.offset_x = mouse_x - (mouse_x - self.offset_x) * ratio
        self.offset_y = mouse_y - (mouse_y - self.offset_y) * ratio
        self.scale = new_scale

        self.redraw()

    def _on_mouse_wheel(self, event):
        """處理滑鼠滾輪縮放"""
        if not self.display_image:
            return
        factor = 1.15 if event.delta > 0 else 0.85
        self._zoom_at(event.x, event.y, factor)

    def _on_button_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = True

    def _on_mouse_drag(self, event):
        if not self._is_dragging or not self.display_image:
            return
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self._drag_start_x = event.x
        self._drag_start_y = event.y

        self.offset_x += dx
        self.offset_y += dy
        if self.image_id:
            self.coords(self.image_id, self.offset_x, self.offset_y)

    def _on_button_release(self, event):
        self._is_dragging = False

    def _on_resize(self, event):
        self._center_empty_text()

    def _center_empty_text(self):
        cw = max(10, self.winfo_width())
        ch = max(10, self.winfo_height())
        self.coords(self._empty_text_id, cw / 2, ch / 2)


class BatchConvertDialog(tk.Toplevel):
    """
    批次轉檔設定與執行對話框
    """

    def __init__(self, parent, default_files: Optional[List[str]] = None, default_dir: Optional[str] = None):
        super().__init__(parent)
        self.title("📦 HEIC 批次轉檔工具")
        self.geometry("780x560")
        self.minsize(680, 480)
        self.configure(bg="#2b2b2b")

        # 置頂與模態
        self.transient(parent)
        self.grab_set()

        self.task: Optional[BatchConvertTask] = None
        self.file_list: List[str] = list(default_files) if default_files else []
        self.output_dir = default_dir or ""

        self._setup_ui()
        if self.file_list:
            self._refresh_file_tree()

    def _setup_ui(self):
        style = ttk.Style(self)
        
        # 主版面容器
        main_frame = tk.Frame(self, bg="#2b2b2b", padx=16, pady=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 來源檔案管理列
        src_frame = tk.LabelFrame(main_frame, text=" 來源檔案清單 ", bg="#2b2b2b", fg="#e0e0e0", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        src_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 按鈕列
        btn_row = tk.Frame(src_frame, bg="#2b2b2b")
        btn_row.pack(fill=tk.X, pady=(0, 6))

        tk.Button(btn_row, text="➕ 新增檔案...", command=self._add_files, bg="#3c3f41", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="📁 新增資料夾...", command=self._add_folder, bg="#3c3f41", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_row, text="🗑️ 清除清單", command=self._clear_files, bg="#503333", fg="#ffffff", relief=tk.FLAT, padx=8, pady=3).pack(side=tk.LEFT, padx=(0, 6))
        
        self.file_count_lbl = tk.Label(btn_row, text="待轉檔項目: 0 個檔案", bg="#2b2b2b", fg="#aaaaaa", font=("Segoe UI", 9))
        self.file_count_lbl.pack(side=tk.RIGHT)

        # 檔案 Treeview 清單
        tree_container = tk.Frame(src_frame, bg="#2b2b2b")
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "size", "status")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=6)
        self.tree.heading("name", text="檔案名稱 / 路徑")
        self.tree.heading("size", text="大小")
        self.tree.heading("status", text="狀態")
        self.tree.column("name", width=420)
        self.tree.column("size", width=90, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. 轉檔選項設定區
        opt_frame = tk.LabelFrame(main_frame, text=" 轉檔與輸出設定 ", bg="#2b2b2b", fg="#e0e0e0", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        opt_frame.pack(fill=tk.X, pady=(0, 10))

        # 目標格式與品質
        row1 = tk.Frame(opt_frame, bg="#2b2b2b")
        row1.pack(fill=tk.X, pady=4)

        tk.Label(row1, text="輸出格式：", bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="JPEG")
        tk.Radiobutton(row1, text="JPEG (.jpg)", variable=self.format_var, value="JPEG", command=self._toggle_quality, bg="#2b2b2b", fg="#ffffff", selectcolor="#444444", activebackground="#2b2b2b").pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(row1, text="PNG (.png - 無失真)", variable=self.format_var, value="PNG", command=self._toggle_quality, bg="#2b2b2b", fg="#ffffff", selectcolor="#444444", activebackground="#2b2b2b").pack(side=tk.LEFT, padx=6)

        # JPEG 品質滑桿
        self.quality_frame = tk.Frame(row1, bg="#2b2b2b")
        self.quality_frame.pack(side=tk.LEFT, padx=(20, 0))
        tk.Label(self.quality_frame, text="JPEG 品質：", bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT)
        self.quality_var = tk.IntVar(value=92)
        self.quality_scale = tk.Scale(self.quality_frame, from_=50, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, bg="#2b2b2b", fg="#ffffff", highlightthickness=0, length=120, command=self._update_quality_lbl)
        self.quality_scale.pack(side=tk.LEFT, padx=4)
        self.quality_val_lbl = tk.Label(self.quality_frame, text="92%", bg="#2b2b2b", fg="#4caf50", width=4)
        self.quality_val_lbl.pack(side=tk.LEFT)

        # 保留 EXIF 選項
        self.exif_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text="保留 EXIF 拍攝時間/相機資訊", variable=self.exif_var, bg="#2b2b2b", fg="#ffffff", selectcolor="#444444", activebackground="#2b2b2b").pack(side=tk.RIGHT)

        # 輸出路徑列
        row2 = tk.Frame(opt_frame, bg="#2b2b2b")
        row2.pack(fill=tk.X, pady=4)

        tk.Label(row2, text="輸出資料夾：", bg="#2b2b2b", fg="#ffffff").pack(side=tk.LEFT)
        self.outdir_var = tk.StringVar(value=self.output_dir)
        self.outdir_entry = tk.Entry(row2, textvariable=self.outdir_var, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.outdir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        tk.Button(row2, text="選擇目錄...", command=self._choose_output_dir, bg="#3c3f41", fg="#ffffff", relief=tk.FLAT, padx=6).pack(side=tk.RIGHT)

        # 3. 進度與控制列
        prog_frame = tk.Frame(main_frame, bg="#2b2b2b")
        prog_frame.pack(fill=tk.X, pady=(0, 4))

        self.progress_bar = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))

        status_row = tk.Frame(prog_frame, bg="#2b2b2b")
        status_row.pack(fill=tk.X)
        self.status_lbl = tk.Label(status_row, text="準備就緒", bg="#2b2b2b", fg="#aaaaaa", font=("Segoe UI", 9))
        self.status_lbl.pack(side=tk.LEFT)
        self.pct_lbl = tk.Label(status_row, text="0%", bg="#2b2b2b", fg="#4caf50", font=("Segoe UI", 9, "bold"))
        self.pct_lbl.pack(side=tk.RIGHT)

        # 底部動作按鈕
        action_frame = tk.Frame(main_frame, bg="#2b2b2b", pady=6)
        action_frame.pack(fill=tk.X)

        self.start_btn = tk.Button(action_frame, text="🚀 開始批次轉檔", command=self._start_conversion, bg="#2e7d32", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=16, pady=6)
        self.start_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.cancel_btn = tk.Button(action_frame, text="停止", command=self._cancel_conversion, bg="#c62828", fg="#ffffff", font=("Segoe UI", 10), relief=tk.FLAT, padx=12, pady=6, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.open_dir_btn = tk.Button(action_frame, text="📂 開啟輸出資料夾", command=self._open_output_folder, bg="#3c3f41", fg="#ffffff", font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=6, state=tk.DISABLED)
        self.open_dir_btn.pack(side=tk.LEFT)

    def _toggle_quality(self):
        if self.format_var.get() == "JPEG":
            self.quality_scale.configure(state=tk.NORMAL)
            self.quality_val_lbl.configure(fg="#4caf50")
        else:
            self.quality_scale.configure(state=tk.DISABLED)
            self.quality_val_lbl.configure(fg="#666666")

    def _update_quality_lbl(self, val):
        self.quality_val_lbl.configure(text=f"{val}%")

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="選擇 HEIC 圖片檔案",
            filetypes=[("HEIC / 支援格式", "*.heic;*.heif;*.jpg;*.jpeg;*.png"), ("所有檔案", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
            self._refresh_file_tree()

    def _add_folder(self):
        folder = filedialog.askdirectory(title="選擇包含 HEIC 圖片的資料夾")
        if folder:
            imgs = scan_directory_images(folder)
            for f in imgs:
                if f not in self.file_list:
                    self.file_list.append(f)
            if not self.outdir_var.get():
                self.outdir_var.set(folder)
            self._refresh_file_tree()

    def _clear_files(self):
        self.file_list.clear()
        self._refresh_file_tree()

    def _choose_output_dir(self):
        dir_path = filedialog.askdirectory(title="選擇轉檔輸出儲存資料夾")
        if dir_path:
            self.outdir_var.set(dir_path)

    def _refresh_file_tree(self):
        self.tree.delete(*self.tree.get_children())
        for f in self.file_list:
            try:
                sz = format_file_size(os.path.getsize(f))
            except Exception:
                sz = "-"
            self.tree.insert("", tk.END, values=(os.path.basename(f), sz, "等待轉換"))
        
        self.file_count_lbl.configure(text=f"待轉檔項目: {len(self.file_list)} 個檔案")
        if self.file_list and not self.outdir_var.get():
            self.outdir_var.set(os.path.dirname(self.file_list[0]))

    def _start_conversion(self):
        if not self.file_list:
            messagebox.showwarning("提示", "請先新增要轉換的圖片檔案！", parent=self)
            return

        out_dir = self.outdir_var.get().strip()
        if not out_dir:
            out_dir = os.path.dirname(self.file_list[0])
            self.outdir_var.set(out_dir)

        os.makedirs(out_dir, exist_ok=True)

        self.start_btn.configure(state=tk.DISABLED)
        self.cancel_btn.configure(state=tk.NORMAL)
        self.open_dir_btn.configure(state=tk.DISABLED)
        self.progress_bar["maximum"] = len(self.file_list)
        self.progress_bar["value"] = 0

        # 重設清單狀態
        children = self.tree.get_children()
        for item in children:
            vals = list(self.tree.item(item, "values"))
            vals[2] = "等待轉換..."
            self.tree.item(item, values=vals)

        self.task = BatchConvertTask(
            file_list=self.file_list,
            output_dir=out_dir,
            output_format=self.format_var.get(),
            quality=self.quality_var.get(),
            keep_exif=self.exif_var.get(),
            max_workers=4,
            on_progress=self._on_item_progress,
            on_finished=self._on_task_finished
        )
        self.task.start()

    def _on_item_progress(self, current: int, total: int, filename: str, success: bool, msg: str):
        def _update():
            self.progress_bar["value"] = current
            pct = int((current / total) * 100)
            self.pct_lbl.configure(text=f"{pct}%")
            self.status_lbl.configure(text=f"正在轉換 ({current}/{total}): {filename}")

            # 更新 Treeview 狀態
            children = self.tree.get_children()
            for item in children:
                vals = list(self.tree.item(item, "values"))
                if vals[0] == filename:
                    vals[2] = "✅ 成功" if success else f"❌ {msg}"
                    self.tree.item(item, values=vals)
                    break

        self.after(0, _update)

    def _on_task_finished(self, success_cnt: int, fail_cnt: int, total: int):
        def _update():
            self.start_btn.configure(state=tk.NORMAL)
            self.cancel_btn.configure(state=tk.DISABLED)
            self.open_dir_btn.configure(state=tk.NORMAL)
            self.status_lbl.configure(text=f"轉檔完成！成功: {success_cnt} 個，失敗: {fail_cnt} 個")

            if fail_cnt == 0:
                messagebox.showinfo("轉檔成功", f"🎉 恭喜！全部 {success_cnt} 個檔案已順利轉換完成！", parent=self)
            else:
                messagebox.showwarning("轉檔結束", f"轉檔完成，其中成功 {success_cnt} 個，失敗 {fail_cnt} 個。", parent=self)

        self.after(0, _update)

    def _cancel_conversion(self):
        if self.task and self.task.is_running():
            self.task.cancel()
            self.status_lbl.configure(text="正在停止轉檔作業...")
            self.cancel_btn.configure(state=tk.DISABLED)

    def _open_output_folder(self):
        out_dir = self.outdir_var.get().strip()
        if out_dir and os.path.exists(out_dir):
            os.startfile(out_dir)
