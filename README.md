# Детекция ГРЗ в реальном времени с использованием ИИ
![](https://img.shields.io/badge/Forum-ВолгаIT-green)
>  Пайплайн определения номера ГРЗ
---
# Содержание
- [О разработчике](#о-разработчике)
- [Стек](#стек)
- [Данные](#данные)
- [Модель](#модель)
- [Обучение](#обучение)
- [Тест](#тестирование-модели)
- [Внедрение модели](#внедрение-модели)
    - [Flask](#простое-flask-api-для-определения-1-картинки-тест)
    - [RTCP](#обработка-видеопотока-rtcp)
---
## О разработчике
| Имя | GitHub | Задачи                           |
|-----|----|----------------------------------|
| Кравченко Алексей | [atlaso4ek](https://github.com/ATLASO4EK "Кравченко Алексей") | Data Science, ML/AI, Flask, RTCP |

---
## Стек
![](https://img.shields.io/badge/Python_3.10-darkred)
![](https://img.shields.io/badge/PyTorch-moccasin)
![](https://img.shields.io/badge/ultralytics-moccasin)
![](https://img.shields.io/badge/pandas-moccasin)
![](https://img.shields.io/badge/flask-moccasin)
---
## Данные
Датасет был взят из открытых источников [ссылка](https://www.kaggle.com/datasets/kirillpribludenko/number-plates-50-russain-50-others)


---
## Модель
В качестве модели для обучения была взята довольно мощная модель детекции объектов Yolo11.

---
## Обучение
Скрипты обучения предоставлены в этом репозитории в директории src/YOLO/train

После обучения на полученных данных, получили вот такой график:
[![results.png](https://i.postimg.cc/vHxqm6mF/results.png)](https://postimg.cc/7fDMsh7m)

---
## Тестирование модели
Скрипты теста модели предоставлены в этом репозитории в директории src/YOLO/test

Некоторые изображения:
[![photo.jpg](https://i.postimg.cc/J7ZKVC6F/photo.jpg)](https://postimg.cc/vD85fkd7)
[![image.png](https://i.postimg.cc/5tD5Ts8R/image.png)](https://postimg.cc/p9YnnYGf)

---
## Внедрение модели
### Простое Flask-api для определения 1 картинки (тест)
[В разработке]

### Обработка видеопотока (RTCP)
[В разработке]