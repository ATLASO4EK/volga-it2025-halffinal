import io

import requests
import json
from PIL import Image
import base64

# Ссылка на запрос
url = 'http://127.0.0.1:8000/api/v1/analyze'

# Отправка файлов в запрос
params = {}
params['file'] = open('photo.jpg','rb').read()
size = Image.open('photo.jpg').size

# Получение ответа
response = requests.get(url, files=params)

# Преобразуем и открываем ответ
resp_str = response.content.decode('utf-8') # преобразуем ответ в строковый формат
resp_list = json.loads(resp_str)    # преобразуем в list
resp_img_bytes = resp_list[0][1:]   # берем первый объект в листе и убираем из него символ b
resp_decoded = base64.b64decode(resp_img_bytes)     # преобразуем в байты
img = Image.frombytes('RGB', size, resp_decoded)    # получаем картинку
img.show()  # открываем