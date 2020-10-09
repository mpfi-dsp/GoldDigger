# GoldDigger Server

This repository contains the code to have a working local server for GoldDigger.

## Instructions:

1. Install nvidia docker:  
    https://github.com/NVIDIA/nvidia-docker

2. Download this github repository and extract it into a folder

3. Download the two models and put them in these folders:
    - media/PIX2PIX/checkpoints/43kGoldDigger/  
    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EYAW60h1luRGmW-Qqu2lXCIBX2TAxxMuLrrowH2vpyMIuA?e=aSGdKm

    - media/PIX2PIX/checkpoints/87kGoldDigger/  
    https://maxplanckflorida.sharepoint.com/:u:/s/dsp-tm/EcTS95eKY9JOsBXFnqlUj70Btlyrm3cbPlMXaRCqzPt0Ng?e=IPQDr1
    
3. In terminal, navigate to the main golddigger directory and build the docker image with the following command:

```
sh build.sh
```
4. Run the docker container:
```
sh run_docker.sh
```

6. In your browser, go to   
    http://0.0.0.0:8000

7. Give yourself a high five.