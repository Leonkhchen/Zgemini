import os
import cv2
import numpy as np

# Load snippets and analyze color signatures
debug_dir = r"C:\Zgemini\exam\debug_analysis"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    img = cv2.imread(os.path.join(r"C:\Zgemini\exam", fname))
    
    # Convert to float and various color spaces
    b, g, r = cv2.split(img.astype(np.float32))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # Analyze red marks: r is significantly higher than g and b
    red_diff = r - np.maximum(g, b)
    print(f"=== {fname} Color Analysis ===")
    print(f"Red diff max: {red_diff.max()}, percent > 20: {(red_diff > 20).mean()*100:.2f}%")
    
    # Analyze blue marks: b is significantly higher than r
    blue_diff = b - r
    print(f"Blue diff max: {blue_diff.max()}, percent > 15: {(blue_diff > 15).mean()*100:.2f}%")
    
    # Analyze green/other colors
    green_diff = g - np.maximum(r, b)
    print(f"Green diff max: {green_diff.max()}, percent > 15: {(green_diff > 15).mean()*100:.2f}%")
    
    # Analyze pure dark printed text vs pencil:
    # Pure dark text: r, g, b are all low (e.g. < 90) and saturation is low (|r-g| < 15, |g-b| < 15)
    dark_mask = (r < 90) & (g < 90) & (b < 90) & (np.abs(r-g) < 20) & (np.abs(g-b) < 20)
    print(f"Dark printed text candidate percent: {dark_mask.mean()*100:.2f}%")
