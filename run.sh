#!bin/bash

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3
sudo apt install python3-pip

## Sound processing packages
sudo apt-get install libsndfile1
pip3 install pysoundfile
pip3 install numpy

## Auth packages
pip3 install jwcrypto
pip3 install pyjwt

## DB packages
pip3 install mysql-connector-python

python3 app.py