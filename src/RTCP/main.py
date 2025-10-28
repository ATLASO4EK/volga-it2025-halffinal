from src.RTCP.ThreadRTCPStream import LicensePlateProcessor
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Обработка RTSP потока для детекции номерных знаков')
    parser.add_argument('--model', type=str, default='best.pt',
                        help='Путь к файлу модели YOLO (default: best.pt)')
    parser.add_argument('--output', type=str, default='output.csv',
                        help='Имя выходного CSV файла (default: output.csv)')

    args = parser.parse_args()

    # Проверка существования файла модели
    if not os.path.exists(args.model):
        print(f"Ошибка: Файл модели {args.model} не найден")
        return

    # Импорт конфигурации из config.py
    try:
        from config import RTSP_URL
    except ImportError:
        print("Ошибка: Создайте файл config.py с переменной RTSP_URL")
        print("Пример содержимого config.py:")
        print("RTSP_URL = 'rtsp://username:password@ip_address:port/stream'")
        return

    # Создание и запуск процессора
    processor = LicensePlateProcessor(
        model_path=args.model,
        rtsp_url=RTSP_URL,
        output_csv=args.output
    )

    processor.run()


if __name__ == "__main__":
    main()