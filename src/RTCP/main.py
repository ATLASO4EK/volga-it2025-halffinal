import cv2
from ultralytics import YOLO
from src.RTCP.ThreadRTCPStream import ThreadedRTSPStream

if __name__ == "__main__":
    rtsp_url = "rtsp://username:password@your_camera_ip:554/stream"
    stream = ThreadedRTSPStream(rtsp_url)

    model = YOLO('best.pt')

    while True:
        frame = stream.get_frame()
        if frame is None:
            continue

        results = model(frame)

        annotated_frame = results[0].plot()

        cv2.imshow('YOLO RTSP Detection', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.stop()
    cv2.destroyAllWindows()