from app import app
from flask import jsonify, request
import base64

from ultralytics import YOLO
from PIL import Image
import numpy as np

@app.route('/api/v1/analyze', methods=['GET'])
def get_preds():
    try:
        # Получаем входные данные (файл картинки или url картинки (в разработке))
        # url = str(request.args.get('url')) if request.args.get('url') is not None else None
        image = request.files['file'] if request.files is not None else None
    except Exception as e:
        print(e)
        return jsonify(str(e)), 400

    # Вносим картинки в массив
    images = []
    '''
    if url:
        response = requests.get(url)
        images.append(Image.open(BytesIO(response.content)))
    '''
    if image:
        images.append(Image.open(image))

    # Если картинок нет - возвращаем ошибку
    if images == []:
        return jsonify('Bad Request: not enough args'), 400

    try:
        # Анализируем картинку и возвращаем результат
        model = YOLO('best.pt')
        results = model(images)

        ans = []
        for result in results:
            ans.append(str(base64.b64encode(Image.fromarray(result.plot()).tobytes())))

        return jsonify(ans), 200
    except Exception as e:
        print(e)
        return jsonify(str(e)), 500
