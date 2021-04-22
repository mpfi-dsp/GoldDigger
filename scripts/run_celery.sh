#!/usr/bin/env bash

REDIS_PORT="$(python -c 'import config;print(config.REDIS_PORT)')"
echo "Redis Port:"
echo $REDIS_PORT

DJANGO_DEV_PORT="$(python -c 'import config;print(config.DJANGO_DEV_PORT)')"
echo "Django Port:"
echo $DJANGO_DEV_PORT

LOCAL_IMAGE_FOLDER="$(python -c 'import config;print(config.LOCAL_IMAGE_FOLDER)')"
echo "Local Image Folder:"
echo $LOCAL_IMAGE_FOLDER

docker stop gold-digger-dev-$DJANGO_DEV_PORT
docker rm gold-digger-dev-$DJANGO_DEV_PORT


docker run  --gpus all \
            -ti \
            --name gold-digger-dev-$DJANGO_DEV_PORT \
            --link redis-$REDIS_PORT:redis \
            -p $DJANGO_DEV_PORT:8000 \
            -p 5555:5555 \
            -v ${PWD}:/usr/src/app \
            -v "/$LOCAL_IMAGE_FOLDER:/usr/src/local-images" \
            gold-digger/gold-digger-dev \
            sh -c "celery -A GoldDigger  worker -l INFO"
