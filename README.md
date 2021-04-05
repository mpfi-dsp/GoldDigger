# GoldDigger Server

This repository contains the code to have a working local server for GoldDigger.

## Instructions:

1. Install nvidia docker:  
    https://github.com/NVIDIA/nvidia-docker

2. Download this github repository and extract it into a folder

3. In terminal, navigate to the main golddigger directory and download the models using this command.
```
sh scripts/download_models.sh
```

If that doesn't work, download them manually and put them in their respective folders folders:

- media/PIX2PIX/checkpoints/43kGoldDigger/  

    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EYAW60h1luRGmW-Qqu2lXCIBX2TAxxMuLrrowH2vpyMIuA?e=aSGdKm

- media/PIX2PIX/checkpoints/87kGoldDigger/  

    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EcTS95eKY9JOsBXFnqlUj70Btlyrm3cbPlMXaRCqzPt0Ng?e=IPQDr1
    
4. Build the docker image with the following command:
```
sh scripts/build.sh
```
5. Manually edit config.py to set the relevant information

6. Run the docker container:  
    - detached (if you don't need to see all the terminal outputs):
    ```
    sh scripts/run_docker_detached.sh

    ```
    - full Terminals:
        1. run redis server  
        ```
        sh scripts/run_redis.sh
        ```
        2. run gold digger docker container and start celery (async task manager)
        ```
        sh scripts/run_celery.sh
        
        celery -A GoldDigger worker -l info
        ```
        3. open a new terminal window and run django server
        ```
        scripts/run_django.sh
        ```
        4. open a new terminal window and run flower (to monitor celery processes)
        ```
        sh scritps/run_flower.sh
        ```


7. In your browser, go to   
    http://0.0.0.0:8000

8. Give yourself a high five.

## Troubleshooting:

### To restart the server, just ctrl+c the celery worker terminal and then the django terminal. Then restart the celery worker, and then django.

If you spin up a docker container and it tells you it already exists, you can
look up the running containers
```
docker container ps
```
- stop the running container (in this case, gold-digger-web):
```
docker stop gold-digger-web
```
- remove a container even after it has been stopped
```
docker rm gold-digger-web
```

## TO DO:
- make it so the program doesn't fail when there's a file in the media folder
- make sure image and mask are the same size
- separate program into docker-compose and nvidia-docker
- add volume mount folder to config file