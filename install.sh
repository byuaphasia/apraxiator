#!/bin/bash

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7 python3.7-dev python3-pip python3-setuptools python3-wheel python3-cffi python3-software-properties

## Sound processing packages
sudo apt-get install libsndfile1

## Packages for PDF generation
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

## Python dependencies
python3 -m pip install -r requirements.txt