#!/usr/bin/env bash
DJANGO_DEV_PORT="$(python -c 'import config;print(config.DJANGO_DEV_PORT)')"
echo "Django Port:"
echo $DJANGO_DEV_PORT

docker exec -d gold-digger-dev-$DJANGO_DEV_PORT sh -c "python3 manage.py makemigrations"
docker exec -d gold-digger-dev-$DJANGO_DEV_PORT sh -c "python3 manage.py migrate"
docker exec -d gold-digger-dev-$DJANGO_DEV_PORT sh -c "python3 manage.py runserver 0.0.0.0:8000"