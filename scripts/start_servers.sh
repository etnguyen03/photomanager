#!/bin/bash

tmux new-session -s servers "bash --init-file <(cd /home/vagrant/photomanager && pipenv run celery -A photomanager worker -l INFO)" \; \
  split-window -h "bash --init-file <(cd /home/vagrant/photomanager && pipenv run gunicorn photomanager.wsgi -b 0.0.0.0:8000)"