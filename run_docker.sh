#!/usr/bin/env bash
docker run -p 8000:8000 -ti -v ${PWD}:/project/ dsp-user/gold-digger-server:latest
