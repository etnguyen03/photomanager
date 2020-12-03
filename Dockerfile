FROM python:3.8-buster

COPY . /app
WORKDIR /app

RUN pip install pipenv && \
    pipenv install --deploy --system

EXPOSE 8000
VOLUME /data
VOLUME /app/photomanager/settings/secret.py

ENTRYPOINT /app/scripts/docker-entrypoint.sh