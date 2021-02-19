import pytest

from PIL.PngImagePlugin import PngImageFile

from pdf_render.utils.image import reformat_image


@pytest.fixture
def image(fixtures_dir):
    file_path = fixtures_dir / "png" / "sample_1.png"
    with file_path.open("rb") as fp:
        yield PngImageFile(fp=fp)


class TestReformatImage:
    def test_size_change(self, image):
        max_size = (200, 200)
        formatted = reformat_image(image, max_size, 0)
        assert formatted.size <= image.size

    def test_contrast_normalization(self, image):
        # TODO:
        pass
