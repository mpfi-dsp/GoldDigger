# GoldDigger Server

_**⚠️ This project is no longer officially supported. We are unable to provide assistance in regards to troubleshooting.**_

This repository contains the code to have a working local server for GoldDigger.
Gold Digger runs via Django Webserver and currently has static IP of 10.203.1.222 assigned - the Machine Name is DS-LAB-WS04.
Make sure config.py in the /scripts folder has the correct IP address and image folder path.

## Installation Instructions:

1. Install nvidia docker:  
    https://github.com/NVIDIA/nvidia-docker

2. Download this github repository and extract it into a folder.

3. In terminal, navigate to the main GoldDigger directory and download the models using this command.
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
5. Manually edit config.py to set the relevant information (ALLOWED_HOSTS, LOCAL_IMAGE_FOLDER)
```
ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1',
    '10.203.1.222', # IP Address of Hosting Computer
    'localhost',
    ]
LOCAL_IMAGE_FOLDER = "/home/MPFI.ORG/stuarte/Desktop/Drives/ds-prog/EM-DATA/gd-for-analysis"
VERSION_NUMBER = "1.09.00"
DJANGO_DEV_PORT = "8001"
REDIS_PORT = "6380
```

6. Run the docker container: (these scripts are to run GD webtool each time after the previous setup instructions are completed) 
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
        4. open a new terminal window and run flower (to monitor celery processes, usually not needed)
        ```
        sh scripts/run_flower.sh
        ```


7. In your browser, go to   
    http://0.0.0.0:8000

8. Give yourself a high five.

## Start GoldDigger Server after Restart
After a computer restart you may need to pull the sources from github with 'git pull'. You may also want to run 'git stash' then 'git checkout master' followed by 'git pull' if you want to switch back to the Master repository.

If you updated the models you would need to run from the GoldDigger diretory

```
sudo sh scripts/download_models.sh
sudo sh scripts/build.sh
```

If the shared drive directories are not mounted correctly, double-click on the 'mount-drives.sh' icon on the desktop. This will mount the shared drives into the directory 'ds-prog' which should make it visible to Gold-Digger.

Make sure LOCAL config.py has the following path information:
LOCAL_IMAGE_FOLDER = "/home/mpfi.org/db-lab-adm/Desktop/Drives/ds-prog/EM-DATA/gd-for-analysis"

Change working Directory to GoldDigger 
```
cd ~/Desktop/GoldDigger
```
Make sure you run the commands from inside the GoldDigger folder - otherwise might give errors):
```
sudo sh scripts/run_docker_detached.sh
```
This should get Gold Digger Webtool up and running on https://10.203.1.222:8001




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

- make sure image and mask are the same size
- separate program into docker-compose and nvidia-docker
