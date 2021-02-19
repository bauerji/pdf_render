import pathlib

import pytest
from rest_framework import status

from pdf_render.app import enums
from pdf_render.app.models import Document, Image


def post_file(fp, client):
    headers = {"HTTP_CONTENT_DISPOSITION": "attachment; filename=file"}
    return client.post(
        "/documents/",
        {"attachment": fp},
        **headers,
    )


@pytest.fixture
def pdf_sample(fixtures_dir):
    filename = fixtures_dir / "pdf" / "sample.pdf"
    with filename.open("rb") as fp:
        yield fp


@pytest.fixture
def create_document_response(db, client, pdf_sample):
    return post_file(pdf_sample, client)


@pytest.fixture
def create_document_and_wait_till_processed(worker, broker, pdf_sample, client):
    response = post_file(pdf_sample, client)
    broker.join("default")
    worker.join()
    return response.json().get("id")


@pytest.fixture
def document_model(db):
    doc = Document()
    doc.save()
    return doc


@pytest.fixture
def image(document_model, fixtures_dir, settings):
    image_name = "sample_1.png"
    document_model.status = enums.DocumentStatus.DONE
    document_model.n_pages = 1
    document_model.save()
    file = fixtures_dir / "png" / image_name
    with file.open("rb") as fp:
        image = Image(page_num=1, document=document_model)
        image.image.save(
            pathlib.Path(settings.APP_IMAGE_STORAGE_PATH) / image_name,
            fp,
            save=True,
        )
    return image


@pytest.fixture
def retrieve_image_response(image, document_model, client):
    return client.get(f"/documents/{document_model.id}/pages/{image.page_num}/")


@pytest.fixture
def retrieve_document_response(document_model, client):
    return client.get(f"/documents/{document_model.id}/")


@pytest.mark.django_db(transaction=True)
class TestDocumentApi:
    def test_create_is_alive(self, create_document_response):
        assert create_document_response.status_code == status.HTTP_201_CREATED

    def test_create_id(self, create_document_response):
        isinstance(create_document_response.json()["id"], int)

    def test_create_creates_model(self, create_document_response):
        id_ = create_document_response.json()["id"]
        assert Document.objects.get(id=id_)

    def test_retrieve_is_alive(self, retrieve_document_response):
        assert retrieve_document_response.status_code == status.HTTP_200_OK

    def test_retrieve_nonexistent_status(self, client):
        response = client.get("/documents/999999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_response(self, retrieve_document_response, document_model):
        expected_response = {
            "status": document_model.status.name.lower(),
            "n_pages": document_model.n_pages,
        }
        assert retrieve_document_response.json() == expected_response

    def test_create_and_retrieve_status_changes(
        self, client, create_document_and_wait_till_processed
    ):
        doc_id = create_document_and_wait_till_processed
        response = client.get(f"/documents/{doc_id}/")
        assert response.json()["status"] == enums.DocumentStatus.DONE.name.lower()
        assert response.json()["n_pages"] is not None


@pytest.mark.django_db(transaction=True)
class TestImageApi:
    def test_retrieve_nonexistent(self, client):
        response = client.get("/documents/9999/pages/999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_status(self, retrieve_image_response):
        assert retrieve_image_response.status_code == status.HTTP_200_OK

    def test_retrieve_image_size_is_equal(self, retrieve_image_response, image):
        content = b"".join(retrieve_image_response.streaming_content)
        assert len(content) == image.image.file.size
