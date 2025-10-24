import cv2
import threading

class ThreadedRTSPStream:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        # Используем FFmpeg как бэкенд для лучшей декодирования RTSP[citation:9]
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        # Запускаем поток для постоянного обновления кадров
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        self.cap.release()