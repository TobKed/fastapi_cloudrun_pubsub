from enum import StrEnum
from enum import auto


class ImageThumbnailsGenerationStatus(StrEnum):
    PENDING = auto()
    QUEUED = auto()
    SUCCESS = auto()
    ERROR = auto()

    def is_done(self) -> bool:
        return self in (self.SUCCESS, self.ERROR)

    def is_queued(self) -> bool:
        return self == self.QUEUED

    def is_not_pending(self) -> bool:
        return self != self.PENDING
