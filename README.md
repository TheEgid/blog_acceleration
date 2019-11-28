# Блог им. Юрия Григорьевича

Блог о коммерческом успехе Юрия Григорьевича. Делюсь советами по бизнесу, жизни и о воспитании детей.

<img src="https://github.com/TheEgid/blog_acceleration/blob/master/sensive-blog/screenshots/site.png"/>

## Запуск

- Скачайте код
- Установите зависимости командой `pip install -r requirements.txt`
- Создайте БД командой `python manage.py migrate`
- Запустите сервер командой `python manage.py runserver`

## Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `manage.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны 3 переменные:
- `DEBUG` — дебаг-режим. Поставьте `True`, чтобы увидеть отладочную информацию в случае ошибки.
- `SECRET_KEY` — секретный ключ проекта
- `DATABASE_NAME` — путь до базы данных, например: `schoolbase.sqlite3`

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
