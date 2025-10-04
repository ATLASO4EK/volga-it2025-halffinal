# Детекция ГРЗ в реальном времени с использованием ИИ
![](https://img.shields.io/badge/Forum-ВолгаIT-green)
>  Описание
---
# Содержание
- [Стек](#стек)
- [О нас](#о-нас)
---
## Стек
![](https://img.shields.io/badge/Python_3.10-darkred)
![](https://img.shields.io/badge/PyTorch-moccasin)
![](https://img.shields.io/badge/ultralytics-moccasin)
![](https://img.shields.io/badge/pandas-moccasin)
![](https://img.shields.io/badge/flask-moccasin)\
![](https://img.shields.io/badge/PostgreSQL-red)\
![](https://img.shields.io/badge/Docker-coral)
---
## О нас
Мы команда энтузиастов и специалистов в области искусственного интеллекта и разработки ПО:
| Имя | GitHub | Роль | Задачи |
|-----|----|------|-------------------------|
| Кравченко Алексей | [atlaso4ek](https://github.com/ATLASO4EK "Кравченко Алексей") | Тимлид, Backend | SQL, ML, API, TG-bot |

## API
### Описание API
Для повышения модульности проекта и дальнейшей его 
масштабируемости нами было разработано API для связи БД, Backend'а и Frontend'а.

### Документация

Раздел /api/v1/

`jams`
- GET `jams`\
_**Принимает**_:\
_**Возвращает**_:\
массив, содержащий информацию о предсказываемых пробках в текущий и ближайшие 3 часа в формате [[час, баллы], [час, баллы], [час, баллы], [час, баллы]]

`analytics`
- GET `analytics`\
_**Принимает**_:\
table - string, название таблицы из которой будут взяты данные, 'fines' или 'evacuate'\
date_start - string, дата начала периода в формате 'YYYY-MM-DD', опционально\
date_end - string, дата конца периода в формате 'YYYY-MM-DD', опционально\
_**Возвращает**_:\
словарь (Dictionary), содержащий проанализированную информацию из таблицы за выбранный период (опционально) или за все имеющиеся данные в таблице в формате:\
{'sum_trip':sum_trip, 'sum_evac':sum_evac,
'sum_rev':sum_rev, 'per_evac':per_evac, 'avg_rev':avg_rev} \
или \
{'sum_cam':sum_cam, 'sum_des':sum_des, 'sum_fin':sum_fin,
'sum_col':sum_col, 'per_col':per_col,
'per_cam_right':per_cam_right, 'avg_fin_des':avg_fin_des}