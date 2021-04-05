FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y wget unzip curl bzip2 git
RUN apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev \
libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev \
libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev unzip postgresql gcc \
musl-dev

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update
RUN pip install opencv-python
RUN apt-get install python-opencv -y
run pip install wheel flower