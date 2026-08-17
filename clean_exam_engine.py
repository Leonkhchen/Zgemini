import os
import cv2
import numpy as np

def clean_exam_paper(image_path, output_path, debug_prefix=None):
    """
    Advanced multi-stage exam paper cleaner:
    1. Color-space stroke separation (Red ink, Blue ink, Pencil, Smudge)
    2. Background illumination normalization & shadow flattening
    3. Printed typography preservation & contrast enhancement
    """
    # Load original high-res image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    h, w, _ = img.shape
    print(f"Processing {os.path.basename(image_path)} ({w}x{h})...")
    
    # 1. Color Channel Analysis
    b = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    r = img[:, :, 2].astype(np.float32)
    
    # Convert to HSV & LAB
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    
    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # -------------------------------------------------------------
    # STAGE A: Detect Red Pen Marks (Corrections, scores, checks)
    # -------------------------------------------------------------
    # Red has high R compared to G & B, or HSV hue in [0..14] or [165..180]
    red_prominence = r - np.maximum(g, b)
    red_hsv_mask = ((h_channel < 14) | (h_channel > 165)) & (s_channel > 30) & (v_channel > 50)
    red_mask = (red_prominence > 12) | red_hsv_mask
    
    # Dilate red mask slightly to catch anti-aliased stroke edges
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    red_mask_dilated = cv2.dilate(red_mask.astype(np.uint8), kernel_small, iterations=1) > 0
    
    # -------------------------------------------------------------
    # STAGE B: Detect Blue / Cyan Ink (Student handwriting, pen)
    # -------------------------------------------------------------
    blue_prominence = b - r
    blue_hsv_mask = (h_channel >= 85) & (h_channel <= 145) & (s_channel > 25) & (v_channel > 40)
    blue_mask = (blue_prominence > 10) | blue_hsv_mask
    blue_mask_dilated = cv2.dilate(blue_mask.astype(np.uint8), kernel_small, iterations=1) > 0
    
    # -------------------------------------------------------------
    # STAGE C: Detect Any Colored Ink (Pencils, Green, Purple, etc.)
    # -------------------------------------------------------------
    max_c = np.maximum(r, np.maximum(g, b))
    min_c = np.minimum(r, np.minimum(g, b))
    chroma = max_c - min_c
    color_mask = (chroma > 18) & (s_channel > 25)
    color_mask_dilated = cv2.dilate(color_mask.astype(np.uint8), kernel_small, iterations=1) > 0
    
    # Combined handwriting mask for colored pens
    handwriting_color_mask = red_mask_dilated | blue_mask_dilated | color_mask_dilated
    
    # -------------------------------------------------------------
    # STAGE D: Illumination Flattening (Remove page shadows & creases)
    # -------------------------------------------------------------
    # Estimate background paper lighting using large morphological closing
    # Kernel size proportional to resolution (~81 px)
    bg_kernel_size = 75
    bg_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (bg_kernel_size, bg_kernel_size))
    bg_estimate = cv2.morphologyEx(gray, cv2.MORPH_DILATE, bg_kernel)
    bg_estimate = cv2.medianBlur(bg_estimate, 31)
    
    # Normalize gray image by background estimate (removes shadows)
    # Target paper brightness is 255
    normalized = np.clip((gray.astype(np.float32) / np.maximum(bg_estimate.astype(np.float32), 1.0)) * 255.0, 0, 255).astype(np.uint8)
    
    # -------------------------------------------------------------
    # STAGE E: Separate Printed Black Text vs Pencil / Smudge
    # -------------------------------------------------------------
    # Printed black text is dark on the normalized image and has low chroma
    # Pencil is lighter gray (e.g. normalized 120-195)
    
    # First, erase colored handwriting by replacing with pure white
    clean_gray = normalized.copy()
    clean_gray[handwriting_color_mask] = 255
    
    # Adaptive thresholding to capture sharp printed characters
    # Printed text has high local contrast and low absolute luminance
    # Pencil strokes have lower local gradient and higher luminance
    
    # Calculate local gradient magnitude
    grad_x = cv2.Sobel(clean_gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(clean_gray, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
    # Printed text candidates:
    # 1. Dark core: clean_gray < 135
    # 2. Medium dark with strong gradient: clean_gray < 175 and grad_mag > 25
    # 3. Exclude weak pencil strokes and smudge
    printed_mask = ((clean_gray < 130) | ((clean_gray < 165) & (grad_mag > 35))) & (~handwriting_color_mask)
    
    # Clean up isolated single-pixel noise
    clean_printed_mask = cv2.morphologyEx(printed_mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    
    # -------------------------------------------------------------
    # STAGE F: Final High-Quality Output Rendering
    # -------------------------------------------------------------
    # Create pure clean white background (255, 255, 255)
    result = np.full((h, w), 255, dtype=np.uint8)
    
    # Render printed text with anti-aliasing / soft edge for maximum readability
    # For core printed pixels, map to deep rich black [0..40]
    # For anti-aliasing boundary pixels, smoothly interpolate
    char_pixels = clean_printed_mask > 0
    result[char_pixels] = np.clip(clean_gray[char_pixels] * 0.4, 0, 45).astype(np.uint8)
    
    # Smooth edges slightly to look like genuine clean printed paper
    # Soft gaussian blend for anti-aliasing
    smoothed_result = cv2.GaussianBlur(result, (3, 3), 0.5)
    
    # Final threshold curve to guarantee 100% pure white paper background
    final_output = np.where(smoothed_result > 210, 255, smoothed_result).astype(np.uint8)
    
    # Save output
    cv2.imwrite(output_path, final_output)
    print(f"Saved clean exam paper to: {output_path}")
    return final_output

# Test run on all 3 images
output_dir = r"C:\Zgemini\exam\clean_output"
os.makedirs(output_dir, exist_ok=True)

exam_dir = r"C:\Zgemini\exam"
files = ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]

for fname in files:
    in_path = os.path.join(exam_dir, fname)
    out_path = os.path.join(output_dir, f"clean_{fname}")
    clean_exam_paper(in_path, out_path)
