#!/bin/bash

# Zip up everything important for deployment
zip -r apraxiator.zip logs src tests travis.yml __init__.py main.py pytest.ini requirements.txt run.sh uwsgi.ini apx-resources Dockerfile Dockerrun.aws.json