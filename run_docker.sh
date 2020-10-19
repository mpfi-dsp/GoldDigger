#!/usr/bin/env bash
docker run --gpus all -p 8000:8000 -v ${PWD}:/usr/src/app gold-digger/gold-digger-dev
