#!/bin/bash

# Применяем миграции базы данных
python manage.py migrate

# Запускаем сервер Django
python manage.py runserver 0.0.0.0:8000