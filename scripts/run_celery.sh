#!/usr/bin/env bash
docker stop gold-digger-web
docker rm gold-digger-web 

docker run -ti --gpus all --name gold-digger-web --link redis1:redis -p 8000:8000 -v ${PWD}:/usr/src/app gold-digger/gold-digger-dev sh -c "celery -A GoldDigger worker -l info"
