#!/usr/bin/env bash
docker stop redis1
docker stop gold-digger-web
docker rm redis1
docker rm gold-digger-web 

docker run -d --name redis1 redis
docker run --gpus all -ti --name gold-digger-web --link redis1:redis -p 8000:8000 -v ${PWD}:/usr/src/app gold-digger/gold-digger-dev sh -c "python3 manage.py makemigrations"
docker exec -ti gold-digger-web sh -c "python3 manage.py migrate"
docker exec -ti gold-digger-web sh -c "python3 manage.py runserver 0.0.0.0:8000"