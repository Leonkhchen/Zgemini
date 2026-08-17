import os
import cv2
import numpy as np

exam_dir = r"C:\Zgemini\exam"
test_dir = r"C:\Zgemini\exam\test_cleaner_v2"
os.makedirs(test_dir, exist_ok=True)

def process_exam_v2(img_path, out_path):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    print(f"Processing v2: {os.path.basename(img_path)} ({w}x{h})...")
    
    # 1. Color Separation for Red and Blue Pen
    b = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    r = img[:, :, 2].astype(np.float32)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_ch = hsv[:, :, 0]
    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]
    
    # Red Pen Mask: Teacher checks, corrections, scores, circles
    # Red has R noticeably higher than G and B
    red_mask = (r - g > 15) & (r - b > 15) & (s_ch > 25)
    # Also HSV red range
    red_hsv = ((h_ch < 15) | (h_ch > 165)) & (s_ch > 35) & (v_ch > 50)
    is_red = red_mask | red_hsv
    
    # Blue Pen Mask: Student handwriting
    blue_mask = (b - r > 12) & (s_ch > 20)
    blue_hsv = (h_ch >= 85) & (h_ch <= 140) & (s_ch > 30)
    is_blue = blue_mask | blue_hsv
    
    # Colored ink combination
    handwriting_mask = is_red | is_blue
    
    # Dilate handwriting mask slightly (3x3 or 5x5) to eliminate edge halos
    k_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    handwriting_dilated = cv2.dilate(handwriting_mask.astype(np.uint8), k_dilate, iterations=1) > 0
    
    # 2. Inpaint / Replace Colored Handwriting with Local Paper Color
    # Calculate local paper background color using grayscale morphological dilation (size 25)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    local_bg = cv2.morphologyEx(gray, cv2.MORPH_DILATE, np.ones((25, 25), np.uint8))
    
    # Inpainted gray: where handwriting was, fill with local background paper luminance
    inpainted_gray = gray.copy()
    inpainted_gray[handwriting_dilated] = local_bg[handwriting_dilated]
    
    # 3. Adaptive Document Binarization / Contrast Enhancement (Sauvola / Local Mean)
    # Window size proportional to image resolution (~41px on 3000px wide image)
    block_size = 45  # Must be odd
    c_constant = 12   # Threshold offset
    
    # Local adaptive threshold
    binary = cv2.adaptiveThreshold(
        inpainted_gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        c_constant
    )
    
    # 4. Post-processing: Remove isolated single-pixel noise specs
    clean_bin = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    
    # Save test output
    cv2.imwrite(out_path, clean_bin)
    
    # Also save downscaled preview
    preview_scale = 1000.0 / w
    preview = cv2.resize(clean_bin, (1000, int(h * preview_scale)))
    preview_path = os.path.join(test_dir, f"preview_{os.path.basename(out_path)}")
    cv2.imwrite(preview_path, preview)
    
    # Measure text density
    text_ratio = (clean_bin == 0).mean() * 100
    print(f"Result {os.path.basename(out_path)}: Text pixel percentage = {text_ratio:.2f}% (Expected 2% - 8%)")

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    in_p = os.path.join(exam_dir, fname)
    out_p = os.path.join(test_dir, f"clean_v2_{fname}")
    process_exam_v2(in_p, out_p)
