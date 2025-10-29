import cv2
import csv
import time
from datetime import timedelta
from ultralytics import YOLO
import numpy as np
import os
import re
import cv2
import numpy as np
from paddleocr import PaddleOCR


class LicensePlateProcessor:
    def __init__(self, model_path, rtsp_url, output_csv="output.csv"):
        self.model = YOLO(model_path)
        self.rtsp_url = rtsp_url
        self.output_csv = output_csv
        self.cap = None
        self.last_detection_time = 0
        self.detection_interval = 0.2
        self.plate_class_id = 1

        try:
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='ru',
            )
        except Exception as e:
            print(f"Ошибка при инициализации PaddleOCR: {e}")
            self.ocr_engine = PaddleOCR(lang='ru')

        self.init_csv()

    def init_csv(self):
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'plate_num'])

    def connect_to_stream(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise ConnectionError(f"Не удалось подключиться к RTSP потоку: {self.rtsp_url}")

        print(f"Успешное подключение к RTSP потоку")
        return True

    def format_time(self, milliseconds):
        td = timedelta(milliseconds=milliseconds)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = int((td.total_seconds() - total_seconds) * 100)

        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

    def extract_plate_region(self, frame, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        # Обрезка с проверкой границ
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return None

        plate_region = frame[y1:y2, x1:x2]
        return plate_region

    def preprocess_plate_image(self, plate_image):
        if plate_image is None or plate_image.size == 0:
            return None

        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image

        gray = cv2.equalizeHist(gray)

        h, w = gray.shape
        if w > 0:
            scale_factor = 200.0 / w
            new_w = 200
            new_h = int(h * scale_factor)
            resized = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        else:
            resized = gray

        return resized

    def mock_ocr_function(self, plate_image):
        try:
            if len(plate_image.shape) == 3:
                plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB)
            else:
                plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_GRAY2RGB)

            processed_plate = self.enhance_plate_image(plate_rgb)

            result = self.ocr_engine.ocr(processed_plate, cls=True)

            if result is None or not result[0]:
                return "####"

            all_texts = []
            for line in result[0]:
                if len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    if confidence > 0.5:
                        all_texts.append((text, confidence))

            if not all_texts:
                return "####"

            best_text, best_confidence = max(all_texts, key=lambda x: x[1])

            formatted_plate = self.format_plate_number(best_text)

            print(f"PaddleOCR распознал: '{best_text}' -> '{formatted_plate}' (уверенность: {best_confidence:.3f})")
            return formatted_plate

        except Exception as e:
            print(f"Ошибка в PaddleOCR: {e}")
            return "####"

    def enhance_plate_image(self, image):
        try:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(image, -1, kernel)

            lab = cv2.cvtColor(sharpened, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

            h, w = enhanced.shape[:2]
            if w < 100:
                scale = 100.0 / w
                new_w = 100
                new_h = int(h * scale)
                enhanced = cv2.resize(enhanced, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

            return enhanced

        except Exception as e:
            print(f"Ошибка при улучшении изображения: {e}")
            return image

    def format_plate_number(self, text):
        cleaned = re.sub(r'[^A-Za-z0-9А-Яа-я]', '', str(text).upper())

        if not cleaned:
            return "####"

        cyrillic_to_latin = {
            'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H',
            'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'У': 'Y', 'Х': 'X'
        }

        converted = ''
        for char in cleaned:
            if char in cyrillic_to_latin:
                converted += cyrillic_to_latin[char]
            else:
                converted += char

        pattern = r'^[A-Z]?(\d{0,3})[A-Z]{0,2}(\d{0,2})$'
        match = re.match(pattern, converted)

        if not match:
            validated = ''
            for char in converted:
                if char.isalnum():
                    validated += char
                else:
                    validated += '#'

            if len(validated) < 8:
                validated = validated.ljust(8, '#')
            elif len(validated) > 9:
                validated = validated[:9]

            return validated

        return converted

    def is_valid_plate_format(self, plate_number):
        if not plate_number or plate_number.strip() == "":
            return False

        has_letter = any(c.isalpha() for c in plate_number)
        has_digit = any(c.isdigit() for c in plate_number)
        has_hash = '#' in plate_number

        return (has_letter and has_digit) or (has_hash and (has_letter or has_digit))

    def process_frame(self, frame, frame_count, fps):
        current_time = frame_count / fps

        results = self.model(frame, verbose=False)

        plates_processed = 0

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    confidence = box.conf.item()

                    if class_id == self.plate_class_id and confidence > 0.3:
                        bbox = box.xyxy[0].cpu().numpy()

                        plate_region = self.extract_plate_region(frame, bbox)

                        if plate_region is not None:
                            h, w = plate_region.shape[:2]
                            if h < 20 or w < 60:
                                continue

                            processed_plate = self.preprocess_plate_image(plate_region)

                            if processed_plate is not None:
                                plate_number = self.mock_ocr_function(processed_plate)

                                if self.is_valid_plate_format(plate_number):
                                    self.save_detection(current_time * 1000, plate_number, confidence)
                                    plates_processed += 1

                                    print(
                                        f"Обнаружен номер: {plate_number} в {self.format_time(current_time * 1000)} (уверенность: {confidence:.2f})")

        if plates_processed > 0:
            self.last_detection_time = current_time
            print(f"Кадр {frame_count}: обработано {plates_processed} номерных знаков")

        return plates_processed

    def save_detection(self, timestamp_ms, plate_number, confidence=0.0):
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            time_str = self.format_time(timestamp_ms)
            writer.writerow([time_str, plate_number])

    def run(self):
        try:
            if not self.connect_to_stream():
                return

            frame_count = 0
            start_time = time.time()

            print("Начало обработки видео...")

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Не удалось получить кадр из потока")
                    break

                frame_count += 1
                current_time = time.time() - start_time
                fps = frame_count / current_time if current_time > 0 else 0

                self.process_frame(frame, frame_count, fps)

                if frame_count % 100 == 0:
                    print(f"Обработано кадров: {frame_count}, FPS: {fps:.2f}")

        except KeyboardInterrupt:
            print("Обработка прервана пользователем")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        finally:
            if self.cap:
                self.cap.release()
            print(f"Обработка завершена. Результаты сохранены в {self.output_csv}")
