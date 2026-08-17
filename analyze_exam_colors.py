import os
import cv2
import numpy as np

exam_dir = r"C:\Zgemini\exam"
debug_dir = r"C:\Zgemini\exam\debug_analysis"
os.makedirs(debug_dir, exist_ok=True)

files = ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]

for fname in files:
    fpath = os.path.join(exam_dir, fname)
    img = cv2.imread(fpath)
    h, w = img.shape[:2]
    
    # Save a small thumbnail for fast inspection
    thumb = cv2.resize(img, (756, 1008))
    cv2.imwrite(os.path.join(debug_dir, f"thumb_{fname}"), thumb)
    
    # Analyze HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Red detection (Hue 0-10 and 170-180)
    mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([12, 255, 255]))
    mask2 = cv2.inRange(hsv, np.array([168, 50, 50]), np.array([180, 255, 255]))
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # Blue detection (Hue 90-130)
    blue_mask = cv2.inRange(hsv, np.array([90, 40, 40]), np.array([135, 255, 255]))
    
    # Green detection
    green_mask = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
    
    # Save mask thumbnails
    red_thumb = cv2.resize(red_mask, (756, 1008))
    blue_thumb = cv2.resize(blue_mask, (756, 1008))
    cv2.imwrite(os.path.join(debug_dir, f"red_mask_{fname}"), red_thumb)
    cv2.imwrite(os.path.join(debug_dir, f"blue_mask_{fname}"), blue_thumb)
    
    print(f"{fname}: Red pixels count: {np.sum(red_mask > 0)}, Blue pixels count: {np.sum(blue_mask > 0)}")

print("Analysis thumbnails saved in:", debug_dir)
