#!/usr/bin/env bash
python3 manage.py makemigrations
python3 manage.py migrate
# celery -A GoldDigger worker -l info
# python3 manage.py runserver 0.0.0.0:8000
exec "$@"