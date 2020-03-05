#!/bin/bash

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3 python3-dev python3-pip python3-setuptools python3-wheel python3-cffi

## Sound processing packages
sudo apt-get install libsndfile1

## Packages for PDF generation
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

## Python dependencies
pip3 install -r requirements.txt