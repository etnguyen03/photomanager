#!/bin/bash

cd /home/vagrant/photomanager

tmux new-session -s servers "bash --init-file <(cd /home/vagrant/photomanager && sudo pipenv run celery -A photomanager worker -l DEBUG)" \; \
  split-window -h "bash --init-file <(cd /home/vagrant/photomanager && pipenv run ./manage.py runserver 0.0.0.0:8000)" \; \
  selectp -t 0 \; \
  split-window -v "bash --init-file <(cd /home/vagrant/photomanager && pipenv run celery -A photomanager beat -l DEBUG)" \; \
  selectp -t 0
