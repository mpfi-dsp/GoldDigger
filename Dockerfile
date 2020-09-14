FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-runtime
RUN mkdir /project
WORKDIR /project
ADD requirements.txt .
RUN pip install -r requirements.txt

# In terminal, build container using:
# docker build -t projectgroup/project .

# to run,
# docker run -p 8888:8888 --gpus all -v ${PWD}:/project projectgroup/project
