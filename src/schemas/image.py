from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Extra

from src.enums.image import ImageThumbnailsGenerationStatus


class ImageThumbnails(BaseModel):
    image_hash: str
    image_url: str | None = None
    thumbnails: list[str] = []
    status: ImageThumbnailsGenerationStatus

    model_config = ConfigDict(extra=Extra.allow)
