from enum import StrEnum
from enum import auto


class ImageAnnotationsGenerationStatus(StrEnum):
    PENDING = auto()
    QUEUED = auto()
    SUCCESS = auto()
    ERROR = auto()

    def is_done(self) -> bool:
        return self in (self.SUCCESS, self.ERROR)
