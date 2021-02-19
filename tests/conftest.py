import pathlib

import pytest


@pytest.fixture(autouse=True)
def temp_image_storage(settings, tmpdir_factory, monkeypatch):
    tmp_dir = tmpdir_factory.mktemp("images")
    settings.APP_IMAGE_STORAGE_PATH = tmp_dir
    monkeypatch.setattr("pdf_render.app.tasks.BASE_DIR", tmp_dir)


@pytest.fixture(autouse=True, scope="session")
def remove_tmp_dir(tmpdir_factory):
    yield
    tmpdir_factory.getbasetemp().remove()


@pytest.fixture
def fixtures_dir():
    return pathlib.Path().cwd() / "tests" / "fixtures"
