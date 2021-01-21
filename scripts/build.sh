#!/usr/bin/env bash
user="gold-digger"
project="gold-digger-dev"

if [ $# -eq 0 ]
  then
    tag='latest'
  else tag=$1
fi

docker build -t $user/$project:$tag ./docker