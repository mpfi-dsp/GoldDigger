# GoldDigger Server

This repository contains the code to have a working local server for GoldDigger.

## Instructions:

1. install nvidia docker:
  https://github.com/NVIDIA/nvidia-docker

2. Build the docker image
  `docker build -t yourusername/golddigger .`

3. run GoldDigger docker container
  `docker run -p 8000:8000 -ti --gpus all -v ${PWD}:/project yourusername/golddigger`
