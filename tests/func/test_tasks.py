import pytest

from django.core.files.uploadedfile import InMemoryUploadedFile

from pdf_render.app import enums
from pdf_render.app.models import Document, Image
from pdf_render.app.tasks import pdf_to_png, PdfToPngPayload


def create_inmemory_file(file) -> InMemoryUploadedFile:
    return InMemoryUploadedFile(file, None, None, "multipart/form-data", None, "utf-8")


@pytest.fixture
def inmemory_image(fixtures_dir):
    filepath = fixtures_dir / "png" / "sample_1.png"
    with filepath.open("rb") as fp:
        yield create_inmemory_file(fp)


@pytest.fixture
def inmemory_pdf(fixtures_dir):
    filepath = fixtures_dir / "pdf" / "sample.pdf"
    with filepath.open("rb") as fp:
        yield create_inmemory_file(fp)


@pytest.fixture
def document_model(db):
    doc = Document()
    doc.save()
    return doc


@pytest.fixture
def pdf_to_png_called(inmemory_pdf, document_model):
    pdf_to_png(PdfToPngPayload(file=inmemory_pdf, doc_id=document_model.id))


class TestPdfToPng:
    def test_invalid_pdf_fails(self, inmemory_image, document_model):
        pdf_to_png(PdfToPngPayload(file=inmemory_image, doc_id=document_model.id))
        document_model.refresh_from_db()
        assert document_model.status == enums.DocumentStatus.FAILED

    @pytest.mark.usefixtures("pdf_to_png_called")
    def test_creates_images(self, document_model):
        assert Image.objects.filter(document=document_model).exists()

    @pytest.mark.usefixtures("pdf_to_png_called")
    def test_changes_status(self, document_model):
        document_model.refresh_from_db()
        assert document_model.status == enums.DocumentStatus.DONE

    @pytest.mark.usefixtures("pdf_to_png_called")
    def test_number_of_pages_equals_to_number_of_images(self, document_model):
        document_model.refresh_from_db()
        assert (
            Image.objects.filter(document=document_model).count()
            == document_model.n_pages
        )
