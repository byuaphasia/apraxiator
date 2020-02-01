#!/bin/bash

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
pip3 install PyMySQL

## Packages for waiver generation
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip3 install jinja2
pip3 install weasyprint
