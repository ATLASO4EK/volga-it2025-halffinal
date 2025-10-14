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
resp_str = response.content.decode('utf-8')
resp_list = json.loads(resp_str)
resp_img_bytes = resp_list[0]
resp_decoded = base64.b64decode(resp_img_bytes[1:])
img = Image.frombytes('RGB', size, resp_decoded)
img.show()