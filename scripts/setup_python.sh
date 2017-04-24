#!/bin/bash

echo 'Downloading packages...'
sudo apt-get install virtualenv python3.5
pip install virtualenv
echo 'Setting up Virtual environment...'
virtualenv -q -p /usr/bin/python3.5 $1 
echo 'Activating virtualenv...'
source $1/bin/activate 
echo 'Installing all required python packages'
# Packages
pip install -r requirements.txt
deactivate
