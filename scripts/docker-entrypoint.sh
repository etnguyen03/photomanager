#!/bin/sh

cd /app/

./manage.py migrate

celery -A photomanager worker --detach
gunicorn -w 4 -b 0.0.0.0:8000 photomanager.wsgi
