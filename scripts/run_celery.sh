#!/usr/bin/env bash

docker stop gold-digger-web-8001
docker rm gold-digger-web-8001

LOCAL_IMAGE_FOLDER="$(python -c 'import config;print(config.LOCAL_IMAGE_FOLDER)')"
echo "Local Image Folder:"
echo $LOCAL_IMAGE_FOLDER

docker run  --gpus all \
            -ti \
            --name gold-digger-web-8001 \
            --link redis1:redis \
            -p 8001:8001 \
            -v ${PWD}:/usr/src/app \
            -v $LOCAL_IMAGE_FOLDER:/usr/src/local-images \
            gold-digger/gold-digger-dev \
            sh -c "celery -A GoldDigger  worker -l INFO"
