import numpy as np
import torch
from PIL import Image
from ultralytics import YOLO
from config import *
import csv
import datetime

import paddleocr
import re

import easyocr
import cv2
import numpy as np

def recognize_license_plate(image_path):
    reader = easyocr.Reader(['ru', 'en'])

    open_cv_image = np.array(image_path)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)  # Конвертируем в оттенки серого

    results = reader.readtext(
        gray
    )
    try:
        return results[0].text
    except:
        return "########"

def save_detection(plate_number):
    """Сохранение результата в CSV с дополнительной информацией"""
    with open(f'{output_folder}/results.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        writer.writerow([time_str, plate_number])

print('Script Started\n------------')

model = YOLO('best.pt')

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

results = model(video_path if isVideo else RTSP_url, save=False, device=device, stream=True, conf=0.35, classes=[1.])
for result in results:
    boxes = result.boxes
    for box in boxes:
        if box.cls.item() == 1.:
            img_bgr = result.plot()
            xyxy = box[0].xyxy.cpu().numpy().tolist()[0]
            save_detection(recognize_license_plate(Image.fromarray(img_bgr[..., ::-1]).crop(xyxy)))