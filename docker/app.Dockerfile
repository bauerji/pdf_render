FROM python:3.9

WORKDIR /app

COPY requirements requirements

RUN python3 -m pip install -r requirements/prod.txt --no-cache-dir

COPY . .

EXPOSE 8000