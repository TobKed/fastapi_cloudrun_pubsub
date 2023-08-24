from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Extra

from src.enums.image import ImageThumbnailsGenerationStatus


class ImageThumbnails(BaseModel):
    image_hash: str
    thumbnails: list[str]
    status: ImageThumbnailsGenerationStatus

    model_config = ConfigDict(extra=Extra.allow)

    def is_queued(self) -> bool:
        return self.status == ImageThumbnailsGenerationStatus.QUEUED

    def is_done(self) -> bool:
        return self.status in (ImageThumbnailsGenerationStatus.SUCCESS, ImageThumbnailsGenerationStatus.ERROR)
