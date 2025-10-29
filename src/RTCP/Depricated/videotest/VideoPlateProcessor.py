import cv2
import csv
import time
from datetime import timedelta
from ultralytics import YOLO
import numpy as np
import re
from paddleocr import PaddleOCR

class VideoLicensePlateProcessor:
    def __init__(self, model_path, video_path, output_csv="output.csv"):
        self.model = YOLO(model_path)
        self.video_path = video_path
        self.output_csv = output_csv
        self.cap = None

        try:
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='ru',
            )
        except Exception as e:
            print(f"Ошибка при инициализации PaddleOCR: {e}")
            # Резервный вариант с минимальной конфигурацией
            self.ocr_engine = PaddleOCR(lang='ru')

        # Статистика
        self.total_plates_detected = 0
        self.frame_count = 0

        # Инициализация CSV файла
        self.init_csv()

    def init_csv(self):
        """Инициализация CSV файла с заголовками"""
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'plate_num'])

    def connect_to_video(self):
        """Подключение к видеофайлу"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ConnectionError(f"Не удалось открыть видеофайл: {self.video_path}")

        # Получаем информацию о видео
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(f"Успешно открыт видеофайл: {self.video_path}")
        print(f"FPS: {fps:.2f}, Всего кадров: {total_frames}, Длительность: {duration:.2f} сек")
        return True

    def format_time(self, milliseconds):
        """Форматирование времени в формат ММ:СС.мс"""
        td = timedelta(milliseconds=milliseconds)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = int((td.total_seconds() - total_seconds) * 100)

        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

    def extract_plate_region(self, frame, bbox):
        """Извлечение региона номерного знака из кадра"""
        x1, y1, x2, y2 = map(int, bbox)
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return None

        plate_region = frame[y1:y2, x1:x2]
        return plate_region

    def preprocess_plate_image(self, plate_image):
        """Предобработка изображения номерного знака для OCR"""
        try:
            if plate_image is None or plate_image.size == 0:
                return None

            # Конвертация в grayscale
            if len(plate_image.shape) == 3:
                gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_image

            gray = cv2.equalizeHist(gray)

            h, w = gray.shape
            if w > 0 and h > 0:
                scale_factor = 200.0 / w
                new_w = 200
                new_h = int(h * scale_factor)
                if new_h > 0 and new_w > 0:
                    resized = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                else:
                    resized = gray
            else:
                resized = gray

            return resized
        except Exception as e:
            print(f"Ошибка при предобработке изображения: {e}")
            return None

    def enhance_plate_image(self, image):
        """Улучшение изображения номерного знака для лучшего распознавания"""
        try:
            if len(image.shape) == 3:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                sharpened = cv2.filter2D(image, -1, kernel)

                lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                enhanced_lab = cv2.merge([l, a, b])
                enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
                return enhanced
            else:
                # Для grayscale изображений
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(image)
                return enhanced

        except Exception as e:
            print(f"Ошибка при улучшении изображения: {e}")
            return image

    def ocr_function(self, plate_image):
        """
        Функция OCR для распознавания российских номерных знаков с использованием PaddleOCR
        с обработкой возможных ошибок.
        """
        try:
            # Проверка входного изображения
            if plate_image is None or plate_image.size == 0:
                return "####"


            if len(plate_image.shape) == 3:
                plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_BGR2RGB)
            else:
                plate_rgb = cv2.cvtColor(plate_image, cv2.COLOR_GRAY2RGB)


            result = self.ocr_engine.ocr(plate_rgb)


            if not result or not result[0]:
                return "####"

            first_block = result[0]

            if len(first_block) > 0:
                best_text = first_block[0][1][0]  # Текст
                confidence = first_block[0][1][1]  # Уверенность

                if confidence > 0.5:
                    formatted_plate = self.format_plate_number(best_text)
                    print(f"PaddleOCR распознал: '{best_text}' -> '{formatted_plate}' (уверенность: {confidence:.3f})")
                    return formatted_plate

            # Если ни одно условие не выполнено
            return "####"

        except Exception as e:
            print(f"Ошибка в PaddleOCR: {e}")
            return "####"

    def format_plate_number(self, text):
        """Форматирование распознанного текста в стандартный формат российского номера"""
        # Удаляем все пробелы и нежелательные символы
        cleaned = re.sub(r'[^A-Za-z0-9А-Яа-я]', '', str(text).upper())

        if not cleaned:
            return "####"

        # Заменяем кириллические символы на латинские аналоги
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

        # Проверяем соответствие шаблону российского номера
        # Буква-3цифры-2буквы-2цифры или варианты
        pattern = r'^[A-Z]?(\d{0,3})[A-Z]{0,2}(\d{0,2})$'
        match = re.match(pattern, converted)

        if not match:
            # Если не соответствует шаблону, оставляем только буквы и цифры, заменяя неподходящие на #
            validated = ''
            for char in converted:
                if char.isalnum():
                    validated += char
                else:
                    validated += '#'

            # Ограничиваем длину и добавляем # при необходимости
            if len(validated) < 8:
                validated = validated.ljust(8, '#')
            elif len(validated) > 9:
                validated = validated[:9]

            return validated

        # Если соответствует шаблону, форматируем должным образом
        return converted

    def is_valid_plate_format(self, plate_number):
        """Базовая проверка формата номерного знака"""
        if not plate_number or plate_number.strip() == "":
            return False

        # Проверяем, что номер содержит хотя бы один буквенный и один цифровой символ
        # или соответствует формату с решетками (частичное распознавание)
        has_letter = any(c.isalpha() for c in plate_number)
        has_digit = any(c.isdigit() for c in plate_number)
        has_hash = '#' in plate_number

        return (has_letter and has_digit) or (has_hash and (has_letter or has_digit))

    def process_frame(self, frame, frame_count, fps):
        """Обработка одного кадра - анализ всех обнаруженных ГРЗ"""
        current_time = frame_count / fps  # Текущее время в секундах

        # Детекция объектов с помощью YOLO
        results = self.model(frame, verbose=False)

        plates_processed = 0

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    confidence = box.conf.item()

                    # Обрабатываем только номерные знаки (class_id = 1)
                    if class_id == 1 and confidence > 0.3:  # Понижен порог для большего охвата
                        bbox = box.xyxy[0].cpu().numpy()

                        # Извлекаем регион номерного знака
                        plate_region = self.extract_plate_region(frame, bbox)

                        if plate_region is not None:
                            # Проверяем минимальный размер региона
                            if len(plate_region.shape) >= 2:
                                h, w = plate_region.shape[:2]
                                if h < 20 or w < 60:  # Минимальные размеры для читаемого номера
                                    continue

                            # Предобработка для OCR
                            processed_plate = self.preprocess_plate_image(plate_region)

                            if processed_plate is not None:
                                # Распознавание номера
                                plate_number = self.ocr_function(processed_plate)

                                # Проверка на валидность номера
                                if self.is_valid_plate_format(plate_number):
                                    # Запись в CSV
                                    self.save_detection(current_time * 1000, plate_number, confidence)
                                    plates_processed += 1
                                    self.total_plates_detected += 1

                                    print(
                                        f"Обнаружен номер: {plate_number} в {self.format_time(current_time * 1000)} (уверенность: {confidence:.2f})")

        # Статистика по кадру
        if plates_processed > 0:
            print(f"Кадр {frame_count}: обработано {plates_processed} номерных знаков")

        return plates_processed

    def save_detection(self, timestamp_ms, plate_number, confidence=0.0):
        """Сохранение результата в CSV"""
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            time_str = self.format_time(timestamp_ms)
            writer.writerow([time_str, plate_number])

    def run(self):
        """Основной цикл обработки видео"""
        try:
            if not self.connect_to_video():
                return

            frame_count = 0
            start_time = time.time()

            print("Начало обработки видео...")
            print("Для прерывания обработки нажмите Ctrl+C")

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Достигнут конец видеофайла")
                    break

                # Вычисление FPS
                frame_count += 1
                current_time = time.time() - start_time
                fps = frame_count / current_time if current_time > 0 else 0

                # Обработка кадра
                processed_count = self.process_frame(frame, frame_count, fps)

                # Прогресс каждые 100 кадров
                if frame_count % 100 == 0:
                    progress = (frame_count / int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))) * 100
                    print(
                        f"Прогресс: {progress:.1f}% | Кадров: {frame_count} | FPS: {fps:.1f} | Найдено номеров: {self.total_plates_detected}")

        except KeyboardInterrupt:
            print("Обработка прервана пользователем")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        finally:
            if self.cap:
                self.cap.release()
            total_time = time.time() - start_time
            print(f"\nОбработка завершена!")
            print(f"Общее время: {total_time:.2f} сек")
            print(f"Обработано кадров: {frame_count}")
            print(f"Средний FPS: {frame_count / total_time:.2f}" if total_time > 0 else "N/A")
            print(f"Всего обнаружено номерных знаков: {self.total_plates_detected}")
            print(f"Результаты сохранены в {self.output_csv}")

