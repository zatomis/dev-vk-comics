
# Загрузка комикса с сайта https://xkcd.com/ в случайном порядке и публикация его в ВК

Скрипт производит загрузку комикса с сайта https://xkcd.com/ в случайном порядке и публикует его в ВК

## Окружение

### Зависимости

- Python3 версии должен быть установлен в вашей системе, и установлены все зависимости
- Скачайте код с GitHub.
- Установите зависимости командой `pip install -r requirements.txt`
- Создайте файл окружения .env и пропишите в него свои данные

```bash
pip install -r requirements.txt
```

### Переменные окружения

Настройки скрипта **comics.py** берётся из переменных окружения.
Создайте файл `.env` и запишите туда данные в формате: `ПЕРЕМЕННАЯ=значение`.
Доступны 2 переменные:
- `VK_ACCESS_TOKEN=` 
- `VK_GROUP_ID=` 

Поместите файл `.env` рядом с файлом `comics.py`.

## Запуск

```bash

$ python3 comics.py

```

После запуска вы увидите


![img.png](img.png)

## Цель проекта
- Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org)