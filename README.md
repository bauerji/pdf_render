# PDF rendering service
Django app for rendering PDF files into PNG images

## Deployment
- create `.env` file based on `.env.template`
- run `docker-compose --env-file .env up --build`
- app will listen on `8000` port

## REST API endpoints
- POST /documents/
    - uploads a file
    - returns JSON { “id”: “<DOCUMENT_ID>? }
- GET /documents/<DOCUMENT_ID>/
    - returns JSON { “status”: “processing/done”, “n_pages”: NUMBER }
- GET /documents/<DOCUMENT_ID>/pages/<PAGE_NUMBER>/
    - returns rendered image png


## Tests
### Locally
Base in mind that you have to have access to a `PostgreSQL` server and also `poppler` installed
- set ENV with postgresql conf: `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- run `python3 -m pytest`

### Dockerized
- `cd tests`
- `docker-compose up --build --exit-code-from test_app`

## How it works
- API is build using Django rest framework on the top of PostgreSQL
- uploaded files are passed via RabbitMQ to dramatiq workers
- PDF -> PNG is realised using `pdf2image` library
- PNG manipulation is handled by `Pillow` lib
- PNG files are stored in shared volume between Django app and worker containers

### Architecture overview
- Django app - serves API
- Dramatiq workers - image processing
- RabbitMQ - dramatiq broker
- PostgreSQL
