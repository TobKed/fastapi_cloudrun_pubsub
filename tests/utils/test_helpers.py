import pytest

from src.utils.helpers import get_extension_from_filename
from src.utils.helpers import get_format_from_content_type


@pytest.mark.parametrize(
    ("filename", "expected_extension"),
    [
        ("kung.jpeg", ".jpeg"),
        ("foo.jpg", ".jpg"),
        ("panda.gif", ".gif"),
        ("kowalski", ""),
    ],
)
def test_get_extension_from_filename(filename: str, expected_extension: str):
    assert get_extension_from_filename(filename) == expected_extension


@pytest.mark.parametrize(
    ("filename", "expected_format"),
    [
        ("image/jpeg", "jpeg"),
        ("image/gif", "gif"),
        ("image/svg", None),
        ("sthing", None),
    ],
)
def test_get_format_from_content_type(filename: str, expected_format: str):
    assert get_format_from_content_type(filename) == expected_format
