import pytest

from src.enums.image import ImageThumbnailsGenerationStatus


@pytest.mark.parametrize(
    ("status", "expected_done"),
    [
        (ImageThumbnailsGenerationStatus.PENDING, False),
        (ImageThumbnailsGenerationStatus.QUEUED, False),
        (ImageThumbnailsGenerationStatus.SUCCESS, True),
        (ImageThumbnailsGenerationStatus.ERROR, True),
    ],
)
def test_image_thumbnails_generation_status_is_done(status: ImageThumbnailsGenerationStatus, expected_done: bool):
    assert status.is_done() is expected_done
