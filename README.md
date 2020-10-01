# GoldDigger Server

This repository contains the code to have a working local server for GoldDigger.

## Instructions:

1. install nvidia docker:  
    https://github.com/NVIDIA/nvidia-docker

2. Install docker-compose:  
    https://docs.docker.com/compose/install/

3. Download this github repository and extract it into a folder

4. Navigate to that folder and build the docker image

```
docker-compose build
```
5. run the docker container
```
docker-compose up
```

6. In your browser, go to   
    http://127.1.1.0:8000
     