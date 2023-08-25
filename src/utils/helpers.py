import mimetypes
from pathlib import Path


def get_extension_from_filename(filename: str) -> str:
    return Path(filename).suffix


def get_format_from_content_type(content_type: str) -> str | None:
    extension = mimetypes.guess_extension(content_type)
    if extension:
        extension = extension.lstrip(".")
    if extension == "jpg":
        extension = "jpeg"
    return extension
