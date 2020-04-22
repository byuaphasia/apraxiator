#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

if [ -z "$1" ]; then
  echo "Must provide path to apx-resources repository"
  echo "i.e. ./eb_prep.sh ../apx-resources"
  exit -1
else
  echo "copying $1 into $SCRIPT_DIR"
  sudo cp -r $1 $SCRIPT_DIR/ >/dev/null
  echo "removing unnecessary apx-resources files"
  sudo rm -rf $SCRIPT_DIR/apx-resources/.git >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/.idea >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/.vscode >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/ssh_backend.sh >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/.DS_Store >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/.gitignore >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/BackendAccess.pem >/dev/null
  sudo rm -rf $SCRIPT_DIR/apx-resources/test-results/* >/dev/null
fi

echo "zipping contents into apraxiator.zip"
# Zip up everything important for deployment
zip -r apraxiator.zip logs src tests .travis.yml __init__.py main.py pytest.ini requirements.txt run.sh uwsgi.ini apx-resources Dockerfile Dockerrun.aws.json >/dev/null
echo "done"