#!/usr/bin/env bash
docker stop redis1
docker rm redis1
docker run -d --name redis1 redis
