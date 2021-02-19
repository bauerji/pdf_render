FROM python:3.9

RUN apt-get update

RUN apt-get -y install poppler-utils

WORKDIR /app

COPY requirements requirements

RUN python3 -m pip install -r requirements/test.txt

COPY . .
