import os
import cv2
import numpy as np

exam_dir = r"C:\Zgemini\exam"
debug_dir = r"C:\Zgemini\exam\debug_analysis"

files = ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]

for fname in files:
    fpath = os.path.join(exam_dir, fname)
    img = cv2.imread(fpath)
    h, w = img.shape[:2]
    
    # Let's crop center regions and save for visual analysis
    crop_center = img[h//4: 3*h//4, w//4: 3*w//4]
    cv2.imwrite(os.path.join(debug_dir, f"crop_center_{fname}"), crop_center)
    
    # Let's analyze luminance and contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(f"=== {fname} Stats ===")
    print(f"Gray min: {gray.min()}, max: {gray.max()}, median: {np.median(gray)}, mean: {gray.mean():.2f}")
    
    # Paper background estimation via morphological closing or percentile
    # Background illumination estimation using large kernel
    kernel_size = 51
    background = cv2.morphologyEx(gray, cv2.MORPH_DILATE, np.ones((kernel_size, kernel_size), np.uint8))
    background = cv2.medianBlur(background, 21)
    
    # Division normalization (removes uneven lighting and shadows)
    diff = 255 - cv2.absdiff(gray, background)
    norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    cv2.imwrite(os.path.join(debug_dir, f"shadow_removed_{fname}"), cv2.resize(norm, (756, 1008)))
