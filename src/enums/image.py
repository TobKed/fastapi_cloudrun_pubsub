from enum import StrEnum
from enum import auto


class ImageThumbnailsGenerationStatus(StrEnum):
    QUEUED = auto()
    SUCCESS = auto()
    ERROR = auto()
