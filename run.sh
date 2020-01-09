#!bin/bash

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3
sudo apt install python3-pip
sudo apt-get install libsndfile1
pip3 install pysoundfile
pip3 install numpy

python3 app.py