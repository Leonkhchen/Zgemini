import os
import cv2
import numpy as np

# Let's inspect small sections of the test papers to see questions and layout
debug_dir = r"C:\Zgemini\exam\debug_analysis"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    img = cv2.imread(os.path.join(r"C:\Zgemini\exam", fname))
    h, w = img.shape[:2]
    # Save a half-size version
    half = cv2.resize(img, (w//2, h//2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(debug_dir, f"half_{fname}"), half)
