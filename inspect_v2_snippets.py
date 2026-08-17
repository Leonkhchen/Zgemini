import os
import cv2
import numpy as np

test_dir = r"C:\Zgemini\exam\test_cleaner_v2"
inspect_dir = r"C:\Zgemini\exam\test_cleaner_v2\snippets"
os.makedirs(inspect_dir, exist_ok=True)

for fname in ["clean_v2_IMG_8755.png", "clean_v2_IMG_8756.png", "clean_v2_IMG_8757.png"]:
    fpath = os.path.join(test_dir, fname)
    img = cv2.imread(fpath)
    h, w = img.shape[:2]
    
    # Save top header (title, exam name, instructions)
    header = img[0:int(h*0.2), 0:w]
    cv2.imwrite(os.path.join(inspect_dir, f"{fname}_header.png"), cv2.resize(header, (1000, int(header.shape[0]*1000/w))))
    
    # Save mid questions
    mid = img[int(h*0.3):int(h*0.6), 0:w]
    cv2.imwrite(os.path.join(inspect_dir, f"{fname}_mid_questions.png"), cv2.resize(mid, (1000, int(mid.shape[0]*1000/w))))
    
    # Save lower questions
    lower = img[int(h*0.6):int(h*0.9), 0:w]
    cv2.imwrite(os.path.join(inspect_dir, f"{fname}_lower_questions.png"), cv2.resize(lower, (1000, int(lower.shape[0]*1000/w))))

print("Saved snippet blocks for inspection.")
