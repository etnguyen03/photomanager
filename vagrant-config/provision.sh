#!/bin/bash

set -e
cd /home/vagrant/photomanager

sudo apt-get update
sudo apt-get upgrade -y

# Install pip
sudo apt-get -y install python3-pip python3-dev

# Install pipenv
sudo pip3 install pipenv

# Install dependencies and create venv
pipenv install --dev --deploy

# Create /data
sudo mkdir /data
sudo chown vagrant:vagrant /data
