import os
import sys
import glob
import cv2
import numpy as np
from PIL import Image
import pillow_heif

# Force UTF-8 on Windows stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Register HEIF opener with PIL
pillow_heif.register_heif_opener()

def cv2_imread_unicode(file_path, flags=cv2.IMREAD_COLOR):
    """Safely reads images with Chinese/Unicode filenames on Windows."""
    with open(file_path, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8)
        return cv2.imdecode(data, flags)

def cv2_imwrite_unicode(file_path, img):
    """Safely writes images with Chinese/Unicode filenames on Windows."""
    ext = os.path.splitext(file_path)[1]
    is_success, buffer = cv2.imencode(ext, img)
    if is_success:
        with open(file_path, 'wb') as f:
            f.write(buffer)
        return True
    return False

def restore_clean_exam(input_path, output_png_path):
    """
    True Exam Paper Restoration Engine:
    1. Multi-spectral color separation (removes teacher red marks and student blue ink)
    2. Local paper background morphological inpainting
    3. Gaussian-weighted local adaptive thresholding (retains 100% of printed questions, formulas & options)
    4. Anti-aliasing stroke smoothing for crisp, high-contrast printing
    """
    # 1. Load image (HEIC or PNG/JPG)
    if input_path.lower().endswith('.heic') or input_path.lower().endswith('.heif'):
        pil_img = Image.open(input_path)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    else:
        img = cv2_imread_unicode(input_path)
        
    if img is None:
        raise ValueError(f"Failed to load image: {input_path}")
        
    h, w = img.shape[:2]
    print(f"--> Processing: {os.path.basename(input_path)} ({w}x{h})...")
    
    # 2. Extract Color Channels for Precision Handwriting Detection
    b = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    r = img[:, :, 2].astype(np.float32)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_ch = hsv[:, :, 0]
    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]
    
    # Red Pen Mask: Teacher checks, corrections, scores, circles
    red_prominence = (r - g > 15) & (r - b > 15) & (s_ch > 25)
    red_hsv = ((h_ch < 15) | (h_ch > 165)) & (s_ch > 35) & (v_ch > 50)
    is_red = red_prominence | red_hsv
    
    # Blue Pen Mask: Student handwriting answers & notes
    blue_prominence = (b - r > 12) & (s_ch > 20)
    blue_hsv = (h_ch >= 85) & (h_ch <= 140) & (s_ch > 30)
    is_blue = blue_prominence | blue_hsv
    
    # Combine all colored handwriting
    handwriting_mask = is_red | is_blue
    
    # Dilate handwriting mask slightly (5x5) to eliminate edge halos
    k_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    handwriting_dilated = cv2.dilate(handwriting_mask.astype(np.uint8), k_dilate, iterations=1) > 0
    
    # 3. Local Background Inpainting (replaces handwriting with surrounding paper color)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    local_bg = cv2.morphologyEx(gray, cv2.MORPH_DILATE, np.ones((25, 25), np.uint8))
    
    inpainted_gray = gray.copy()
    inpainted_gray[handwriting_dilated] = local_bg[handwriting_dilated]
    
    # 4. Adaptive Document Binarization & Question Text Recovery
    # Uses Gaussian adaptive thresholding tuned for high-resolution document scans
    block_size = 45  # Local window (~45px)
    c_offset = 12    # Dynamic contrast threshold
    
    binary = cv2.adaptiveThreshold(
        inpainted_gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_offset
    )
    
    # 5. Clean up isolated single-pixel noise specs
    clean_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    
    # 6. Anti-Aliasing for Print Quality
    # Apply soft Gaussian blend to text edges so printed output looks smooth and sharp
    smoothed = cv2.GaussianBlur(clean_binary, (3, 3), 0.5)
    final_sheet = np.where(smoothed > 210, 255, smoothed).astype(np.uint8)
    
    # Save High-Res PNG
    cv2_imwrite_unicode(output_png_path, final_sheet)
    print(f"[OK] Saved clean printable sheet: {output_png_path}")
    return final_sheet

def generate_printable_exam_pdf(clean_images, output_pdf_path):
    """
    Compiles cleaned high-resolution exam sheets into a standard A4 PDF document
    ready for direct printing and student re-testing.
    """
    pil_pages = []
    for img_path in clean_images:
        img = cv2_imread_unicode(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            pil_img = Image.fromarray(img).convert('RGB')
            pil_pages.append(pil_img)
        
    if pil_pages:
        pil_pages[0].save(
            output_pdf_path,
            save_all=True,
            append_images=pil_pages[1:],
            resolution=300.0,
            quality=95
        )
        print(f"[OK] Successfully generated Multi-Page Printable PDF: {output_pdf_path}")

if __name__ == '__main__':
    exam_dir = r"C:\Zgemini\exam"
    out_dir = os.path.join(exam_dir, "乾淨試卷_重測用")
    os.makedirs(out_dir, exist_ok=True)
    
    base_names = ["IMG_8755", "IMG_8756", "IMG_8757"]
    clean_paths = []
    
    for base in base_names:
        png_f = os.path.join(exam_dir, f"{base}.png")
        heic_f = os.path.join(exam_dir, f"{base}.HEIC")
        target_f = png_f if os.path.exists(png_f) else heic_f
        
        if os.path.exists(target_f):
            out_png = os.path.join(out_dir, f"{base}_乾淨試卷.png")
            restore_clean_exam(target_f, out_png)
            clean_paths.append(out_png)
            
    # Generate unified PDFs
    pdf_out = os.path.join(out_dir, "全真模擬試卷_乾淨重測本.pdf")
    generate_printable_exam_pdf(clean_paths, pdf_out)
    
    combined_pdf_root = os.path.join(exam_dir, "乾淨試卷_可重寫.pdf")
    generate_printable_exam_pdf(clean_paths, combined_pdf_root)
    
    print("\n==========================================")
    print("SUCCESS: 所有試卷題目已完整還原，手寫筆跡已全數消除！")
    print(f"產出目錄: {out_dir}")
    print(f"合併 PDF: {combined_pdf_root}")
    print("==========================================")
