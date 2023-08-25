from fastapi import HTTPException


class ThumbnailGenerationError(HTTPException):
    pass
