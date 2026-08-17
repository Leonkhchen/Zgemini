import os
import cv2
import numpy as np

exam_dir = r"C:\Zgemini\exam"
debug_dir = r"C:\Zgemini\exam\debug_analysis"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    fpath = os.path.join(exam_dir, fname)
    img = cv2.imread(fpath)
    h, w = img.shape[:2]
    
    # Save 4 quadrant snippets (high resolution) to inspect exact handwriting vs printed text
    q1 = img[h//8:h//8+800, w//8:w//8+1000] # Top-left
    q2 = img[h//2:h//2+800, w//8:w//8+1000] # Mid-left
    q3 = img[h//2:h//2+800, w//2:w//2+1000] # Center-right
    q4 = img[3*h//4:3*h//4+800, w//4:w//4+1000] # Bottom
    
    cv2.imwrite(os.path.join(debug_dir, f"snippet_top_{fname}"), q1)
    cv2.imwrite(os.path.join(debug_dir, f"snippet_mid_{fname}"), q2)
    cv2.imwrite(os.path.join(debug_dir, f"snippet_midright_{fname}"), q3)
    cv2.imwrite(os.path.join(debug_dir, f"snippet_bottom_{fname}"), q4)

print("Saved snippets for detail inspection.")
