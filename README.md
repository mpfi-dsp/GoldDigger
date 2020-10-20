# GoldDigger Server

This repository contains the code to have a working local server for GoldDigger.

## Instructions:

1. Install nvidia docker:  
    https://github.com/NVIDIA/nvidia-docker

2. Download this github repository and extract it into a folder

3. In terminal, navigate to the main golddigger directory and download the models using this command.
```
sh download_models.sh
```

If that doesn't work, download them manually and put them in their respective folders folders:

- media/PIX2PIX/checkpoints/43kGoldDigger/  

    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EYAW60h1luRGmW-Qqu2lXCIBX2TAxxMuLrrowH2vpyMIuA?e=aSGdKm

- media/PIX2PIX/checkpoints/87kGoldDigger/  

    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EcTS95eKY9JOsBXFnqlUj70Btlyrm3cbPlMXaRCqzPt0Ng?e=IPQDr1
    
4. Build the docker image with the following command:
```
sh build.sh
```
5. Manually edit config.py to set the relevant information

6. Run the docker container:  
    - quick (if you don't need to see all the terminal outputs):
    ```
    sh run_docker.sh
    ```
    - full Terminals:
        1. run redis server  
        ```
        docker run -d --name redis1 redis
        ```
        2. run gold digger docker container and start celery (async task manager)
        ```
        docker run -ti --gpus all --name gold-digger-web --link redis1:redis -p 8000:8000 -v ${PWD}:/usr/src/app gold-digger/gold-digger-dev
        
        celery -A GoldDigger worker -l info
        ```
        3. open a new terminal window and run django server
        ```
        docker exec -ti gold-digger-web /bin/bash

        python3 manage.py runserver 0.0.0.0:8000 
        ```


7. In your browser, go to   
    http://0.0.0.0:8000

8. Give yourself a high five.


### TO DO:
- make it clear when files are uploaded
- update user on status of analysis
    - unwrap run.py into separate functions
<<<<<<< HEAD
    - clean it up, make it into a class
- make blue mask
- make it so the program doesn't fail when there's a file in the media folder
=======
- make blue mask
>>>>>>> 8f583b4de75e28de5f8da4044fc5efb333d3c059
