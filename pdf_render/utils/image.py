from typing import Tuple

from io import BytesIO

from PIL.Image import Image
from PIL.ImageFile import ImageFile
from PIL.ImageOps import autocontrast
from django.core.files import File


def reformat_image(
    image: ImageFile, max_size: Tuple[int, int], contrast_cutoff: int
) -> Image:
    image.thumbnail(max_size)
    return autocontrast(image, cutoff=contrast_cutoff)


def prepare_image_for_django(image: Image) -> File:
    img_io = BytesIO()
    image.save(img_io, "PNG")
    return File(img_io)
