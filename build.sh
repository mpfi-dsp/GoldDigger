#!/usr/bin/env bash
user="dsp-user"
project="gold-digger-server"

if [ $# -eq 0 ]
  then
    tag='latest'
  else tag=$1
fi

docker build -t $user/$project:$tag .
