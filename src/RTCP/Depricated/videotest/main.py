import argparse
import os

from VideoPlateProcessor import VideoLicensePlateProcessor

def main():
    parser = argparse.ArgumentParser(description='Обработка видеофайла для детекции номерных знаков')
    parser.add_argument('--video', type=str, required=True,
                        help='Путь к видеофайлу')
    parser.add_argument('--model', type=str, default='best.pt',
                        help='Путь к файлу модели YOLO (default: best.pt)')
    parser.add_argument('--output', type=str, default='detection_results.csv',
                        help='Имя выходного CSV файла (default: detection_results.csv)')

    args = parser.parse_args()

    # Проверка существования файла модели
    if not os.path.exists(args.model):
        print(f"Ошибка: Файл модели {args.model} не найден")
        return

    # Проверка существования видеофайла
    if not os.path.exists(args.video):
        print(f"Ошибка: Видеофайл {args.video} не найден")
        return

    # Создание и запуск процессора
    processor = VideoLicensePlateProcessor(
        model_path=args.model,
        video_path=args.video,
        output_csv=args.output
    )

    processor.run()


if __name__ == "__main__":
    main()