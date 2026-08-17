import os
import cv2
import numpy as np

clean_dir = r"C:\Zgemini\exam\clean_output"
orig_dir = r"C:\Zgemini\exam"
debug_dir = r"C:\Zgemini\exam\debug_analysis"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    orig = cv2.imread(os.path.join(orig_dir, fname))
    clean = cv2.imread(os.path.join(clean_dir, f"clean_{fname}"), cv2.IMREAD_GRAYSCALE)
    
    h, w = orig.shape[:2]
    
    # 1. Background whiteness percentage (pixels > 250)
    white_ratio = (clean > 250).mean() * 100
    black_ratio = (clean < 50).mean() * 100
    gray_noise_ratio = ((clean >= 50) & (clean <= 250)).mean() * 100
    
    print(f"=== Quality Check: {fname} ===")
    print(f"Pure White Paper Background: {white_ratio:.2f}%")
    print(f"Crisp Black Text: {black_ratio:.2f}%")
    print(f"Intermediate/Noise: {gray_noise_ratio:.2f}%")
    
    # Save comparison side-by-side snippet (1200x800)
    # Pick a region with heavy handwriting and corrections
    y0, y1 = h//3, h//3 + 900
    x0, x1 = w//4, w//4 + 1200
    
    orig_crop = orig[y0:y1, x0:x1]
    clean_crop = cv2.cvtColor(clean[y0:y1, x0:x1], cv2.COLOR_GRAY2BGR)
    
    comparison = np.hstack([orig_crop, clean_crop])
    cv2.imwrite(os.path.join(debug_dir, f"compare_{fname}"), comparison)
    print(f"Saved comparison to compare_{fname}")
