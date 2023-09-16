from fastapi import HTTPException


class AnnotationGenerationError(HTTPException):
    pass
