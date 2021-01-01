#!/bin/bash

set -e
cd /home/vagrant/photomanager

sudo apt-get update
sudo apt-get upgrade -y

# Install pip
sudo apt-get -y install python3-pip python3-dev

# Install pipenv
sudo pip3 install pipenv

# face-recognition requires cmake
apt-get -y install cmake

# Install dependencies and create venv
pipenv install --dev --deploy

# Create /data
sudo mkdir -p /data
sudo chown vagrant:vagrant /data

# Create /thumbs
sudo mkdir -p /thumbs
sudo chown vagrant:vagrant /thumbs

# Install and configure Redis
apt-get -y install redis
sed -i 's/^#\(bind 127.0.0.1 ::1\)$/\1/' /etc/redis/redis.conf
sed -i 's/^\(protected-mode\) no$/\1 yes/' /etc/redis/redis.conf
systemctl restart redis-server
systemctl enable redis-server
