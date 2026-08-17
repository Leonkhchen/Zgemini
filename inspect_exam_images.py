import os
import cv2
import numpy as np
from PIL import Image
import pillow_heif

exam_dir = r"C:\Zgemini\exam"
files = ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]

for fname in files:
    fpath = os.path.join(exam_dir, fname)
    if os.path.exists(fpath):
        img = cv2.imread(fpath)
        h, w, c = img.shape
        print(f"=== {fname} ===")
        print(f"Dimensions: {w}x{h}, Channels: {c}")
        # Sample color distribution
        mean_bgr = img.mean(axis=(0,1))
        print(f"Mean BGR: {mean_bgr}")
