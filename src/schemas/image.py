from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Extra

from src.enums.image import ImageAnnotationsGenerationStatus


class ImageAnnotation(BaseModel):
    index: int
    label: str
    confidence: float


class ImageClassification(BaseModel):
    image_hash: str
    image_url: str | None = None
    annotations: list[ImageAnnotation] = []
    status: ImageAnnotationsGenerationStatus

    model_config = ConfigDict(extra=Extra.allow)
