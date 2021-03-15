FROM python:3.7.5-slim

RUN mkdir /server && apt-get update && apt-get install -y git libpq-dev
WORKDIR /server

ADD ./server/requirements/dev.txt /server/requirements.txt
RUN pip install -r requirements.txt
