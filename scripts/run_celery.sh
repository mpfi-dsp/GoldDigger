#!/usr/bin/env bash

docker stop gold-digger-web
docker rm gold-digger-web
docker run --gpus all -ti --name gold-digger-web --link redis1:redis -p 8888:8888 -v ${PWD}:/usr/src/app gold-digger/gold-digger-dev sh -c "celery -A GoldDigger  worker -l INFO"
