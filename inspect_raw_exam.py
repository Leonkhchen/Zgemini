import os
import cv2
import numpy as np

exam_dir = r"C:\Zgemini\exam"
debug_dir = r"C:\Zgemini\exam\debug_inspect"
os.makedirs(debug_dir, exist_ok=True)

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    fpath = os.path.join(exam_dir, fname)
    if not os.path.exists(fpath):
        continue
    img = cv2.imread(fpath)
    h, w, c = img.shape
    print(f"=== {fname} ===")
    print(f"Size: {w}x{h}")
    
    # Save a downscaled thumbnail (1000px width)
    scale = 1000.0 / w
    thumb = cv2.resize(img, (1000, int(h * scale)))
    cv2.imwrite(os.path.join(debug_dir, f"thumb_{fname}"), thumb)
    
    # Let's save 4 high-res crops from different parts of the image
    crops = [
        ("top_header", img[0:int(h*0.25), 0:w]),
        ("q1_area", img[int(h*0.25):int(h*0.5), 0:w]),
        ("q2_area", img[int(h*0.5):int(h*0.75), 0:w]),
        ("bottom_area", img[int(h*0.75):h, 0:w]),
    ]
    for label, crop in crops:
        # Resize crop slightly so it's easy to analyze if needed
        c_h, c_w = crop.shape[:2]
        crop_thumb = cv2.resize(crop, (1200, int(c_h * 1200 / c_w)))
        cv2.imwrite(os.path.join(debug_dir, f"{fname}_{label}.png"), crop_thumb)

    # Analyze pixel values of text vs background
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Histogram of gray
    hist, bins = np.histogram(gray, bins=256, range=[0, 256])
    print(f"Gray percentiles: 5%={np.percentile(gray, 5)}, 10%={np.percentile(gray, 10)}, 50%={np.percentile(gray, 50)}, 90%={np.percentile(gray, 90)}")
    print(f"HSV H mean: {hsv[:,:,0].mean():.1f}, S mean: {hsv[:,:,1].mean():.1f}, V mean: {hsv[:,:,2].mean():.1f}")
