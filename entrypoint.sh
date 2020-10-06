#!/bin/sh

if ["DATABASE"] = "postgres"
then
  echo "Waiting for postgres..."

  while ! nc -z $SWL_HOST $SWL_PORT; do
    sleep 0.1
  done

  echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate

exec "$@"
