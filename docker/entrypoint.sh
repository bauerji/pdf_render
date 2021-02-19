#!/bin/bash

set -e

# wait for postgres to start
while !</dev/tcp/db/${POSTGRES_PORT}; do
  echo "postgres not ready yet"
  sleep 1
done

# wait for rabbitmq to start
while !</dev/tcp/rabbitmq/${RMQ_PORT}; do
  echo "rabbitmq not ready yet"
  sleep 1
done

python3 manage.py migrate

gunicorn pdf_render.wsgi:application --bind 0.0.0.0:8000
