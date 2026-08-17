import os
import cv2
import numpy as np

debug_dir = r"C:\Zgemini\exam\debug_analysis"

# Check the cropped comparisons to see if anything was missed or over-erased
for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    fpath = os.path.join(debug_dir, f"compare_{fname}")
    if os.path.exists(fpath):
        cmp_img = cv2.imread(fpath)
        print(f"Compare image {fname} exists, size: {cmp_img.shape}")
