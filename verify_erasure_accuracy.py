import os
import cv2
import numpy as np

orig_dir = r"C:\Zgemini\exam"
clean_dir = r"C:\Zgemini\exam\test_cleaner_v2"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    orig = cv2.imread(os.path.join(orig_dir, fname))
    clean = cv2.imread(os.path.join(clean_dir, f"clean_v2_{fname}"), cv2.IMREAD_GRAYSCALE)
    
    b, g, r = orig[:,:,0].astype(np.float32), orig[:,:,1].astype(np.float32), orig[:,:,2].astype(np.float32)
    hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
    h_ch, s_ch, v_ch = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    # Red marks
    is_red = (r - g > 15) & (r - b > 15) & (s_ch > 25)
    # Blue marks
    is_blue = (b - r > 12) & (s_ch > 20)
    
    # Red handwriting erasure rate: percentage of original red pixels that are now white (>200) in clean image
    red_total = np.sum(is_red)
    red_erased = np.sum((is_red) & (clean > 200))
    red_erase_rate = (red_erased / red_total * 100) if red_total > 0 else 100.0
    
    # Blue handwriting erasure rate
    blue_total = np.sum(is_blue)
    blue_erased = np.sum((is_blue) & (clean > 200))
    blue_erase_rate = (blue_erased / blue_total * 100) if blue_total > 0 else 100.0
    
    print(f"=== Verification for {fname} ===")
    print(f"Red handwriting total pixels: {red_total}, Erased: {red_erased} ({red_erase_rate:.2f}%)")
    print(f"Blue handwriting total pixels: {blue_total}, Erased: {blue_erased} ({blue_erase_rate:.2f}%)")
    print(f"Overall clean paper background: {(clean == 255).mean()*100:.2f}%")
    print(f"Solid printed question text: {(clean == 0).mean()*100:.2f}%")
