import logging
import pathlib
from typing import TypedDict

import dramatiq
from django.conf import settings
from django.core.files import uploadedfile
from pdf2image import convert_from_bytes
from pdf2image.exceptions import (
    PDFPageCountError,
    PDFPopplerTimeoutError,
    PDFSyntaxError,
)

from . import enums, models
from ..utils.image import prepare_image_for_django, reformat_image

BASE_DIR = pathlib.Path(settings.APP_IMAGE_STORAGE_PATH)
logger = logging.getLogger(__name__)


class PdfToPngPayload(TypedDict):
    file: uploadedfile.InMemoryUploadedFile
    doc_id: int


@dramatiq.actor
def pdf_to_png(payload: PdfToPngPayload):
    file = payload["file"]
    doc_id = payload["doc_id"]
    doc = models.Document.objects.get(id=doc_id)
    try:
        images = convert_from_bytes(file.read(), fmt="png")
    except (PDFPageCountError, PDFPopplerTimeoutError, PDFSyntaxError):
        logger.exception(f"Failed to convert document ({doc_id}), marking as failed.")
        doc.status = enums.DocumentStatus.FAILED
        doc.save()
        return
    for i, img in enumerate(images):
        filename = BASE_DIR / f"{doc_id}_{i+1}.png"
        image_obj = models.Image(page_num=i + 1, document_id=doc_id)
        file = prepare_image_for_django(
            reformat_image(
                img, settings.APP_IMAGE_MAX_SIZE, settings.APP_IMAGE_CONTRAST_CUTOFF
            )
        )
        logger.debug(f"Saving image to: {filename}.")
        image_obj.image.save(filename, file, save=True)
    doc.n_pages = len(images)
    doc.status = enums.DocumentStatus.DONE
    doc.save()
    logger.debug(f"Document {doc_id} done.")
