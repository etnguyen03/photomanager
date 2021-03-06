#!/bin/bash

cd /app/

if [[ "$1" == "daphne" ]]
then
  ./manage.py migrate
  daphne -b 0.0.0.0 -p 8000 photomanager.asgi:application
elif [[ "$1" == "celery" ]]
then
  celery -A photomanager worker
elif [[ "$1" == "celerybeat" ]]
then
  celery -A photomanager beat
else
  exec "$@"
fi