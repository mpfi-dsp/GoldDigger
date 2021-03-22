#!/usr/bin/env bash
REDIS_PORT="$(python -c 'import config;print(config.REDIS_PORT)')"
echo "Redis Port:"
echo $REDIS_PORT

docker stop redis-$REDIS_PORT
docker rm redis-$REDIS_PORT
docker run -d --name redis-$REDIS_PORT redis