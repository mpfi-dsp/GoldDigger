FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y wget unzip curl bzip2 git
RUN apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev \
libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev \
libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev unzip

# removed libjasper-dev

# RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh
# RUN bash Miniconda3-py37_4.8.3-Linux-x86_64.sh -p /miniconda -b
# RUN rm Miniconda3-py37_4.8.3-Linux-x86_64.sh
# ENV PATH=/miniconda/bin:${PATH}
# RUN conda update -y conda


#Make run commands use the conda environment
# SHELL ["conda", "run", "n", "myenv", "/bin/bash", "-c"]


# RUN conda install -y pytorch torchvision -c pytorch
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install opencv-python
RUN apt-get install python-opencv -y





# FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime
# RUN mkdir /usr/src/app
# WORKDIR /usr/src/app
# ADD requirements.txt .
# RUN pip install -r requirements.txt
# RUN add-apt-repository python-opencv
# RUN apt-get install python-opencv -y
