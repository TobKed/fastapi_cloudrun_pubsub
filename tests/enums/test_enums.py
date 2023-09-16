import pytest

from src.enums.image import ImageAnnotationsGenerationStatus


@pytest.mark.parametrize(
    ("status", "expected_done"),
    [
        (ImageAnnotationsGenerationStatus.PENDING, False),
        (ImageAnnotationsGenerationStatus.QUEUED, False),
        (ImageAnnotationsGenerationStatus.SUCCESS, True),
        (ImageAnnotationsGenerationStatus.ERROR, True),
    ],
)
def test_image_thumbnails_generation_status_is_done(status: ImageAnnotationsGenerationStatus, expected_done: bool):
    assert status.is_done() is expected_done
