#!/usr/bin/env bash

docker stop gold-digger-web-8001
docker rm gold-digger-web-8001

docker run  --gpus all \
            -ti \
            --name gold-digger-web-8001 \
            --link redis1:redis \
            -p 8001:8001 \
            -v ${PWD}:/usr/src/app \
            -v ~/Desktop/Network-Drives/ds-prog/EM-DATA/gd-for-analysis:/usr/src/local-images \
            gold-digger/gold-digger-dev \
            sh -c "celery -A GoldDigger  worker -l INFO"
