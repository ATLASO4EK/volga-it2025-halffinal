import os
from ultralytics import YOLO

root = 'D:/pythonic-shit/volga-it2025-halffinal/src/YOLO/test'
os.chdir(root)

model = YOLO('best.pt')

os.chdir(f'{root}/dataset')

results = model(os.listdir())  # return a list of Results objects

# Process results list
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()