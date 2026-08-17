import os
import cv2
import numpy as np

# Let's inspect small zoomed-in regions containing student answers and questions
# on IMG_8755, IMG_8756, IMG_8757 to verify accuracy of erasure
output_dir = r"C:\Zgemini\exam\clean_output"
debug_dir = r"C:\Zgemini\exam\debug_analysis"

for fname in ["IMG_8755.png", "IMG_8756.png", "IMG_8757.png"]:
    orig = cv2.imread(os.path.join(r"C:\Zgemini\exam", fname))
    clean = cv2.imread(os.path.join(output_dir, f"clean_{fname}"))
    
    h, w = orig.shape[:2]
    
    # Let's save 3 distinct zoomed patches (500x500 each) along the vertical axis
    patches = [
        ("top", int(h*0.2), int(w*0.3)),
        ("mid", int(h*0.5), int(w*0.3)),
        ("bot", int(h*0.8), int(w*0.3)),
    ]
    
    for label, py, px in patches:
        py_end = min(h, py + 600)
        px_end = min(w, px + 800)
        
        orig_p = orig[py:py_end, px:px_end]
        clean_p = clean[py:py_end, px:px_end]
        
        side_by_side = np.hstack([orig_p, clean_p])
        cv2.imwrite(os.path.join(debug_dir, f"patch_{fname}_{label}.png"), side_by_side)

print("Saved zoomed-in verification patches.")
