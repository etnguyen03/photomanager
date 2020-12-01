FROM python:3.8-buster

COPY . /app
WORKDIR /app

RUN pip install pipenv && \
    pipenv install --deploy --system

ENTRYPOINT /app/scripts/docker-entrypoint.sh