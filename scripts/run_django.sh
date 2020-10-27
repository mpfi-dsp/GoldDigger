#!/usr/bin/env bash
docker exec -ti gold-digger-web sh -c "python3 manage.py makemigrations"
docker exec -ti gold-digger-web sh -c "python3 manage.py migrate"
docker exec -ti gold-digger-web sh -c "python3 manage.py runserver 0.0.0.0:8000"