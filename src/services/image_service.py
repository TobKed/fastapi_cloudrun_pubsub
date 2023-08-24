import hashlib

from fastapi import Depends
from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError

from src.config import Settings
from src.config import get_settings
from src.schemas.image import ImageThumbnails
from src.services.database_service import DatabaseService


class ImageService:
    collection = "ImageCollection"

    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        database_service: DatabaseService = Depends(DatabaseService),
    ) -> None:
        self.settings = settings
        self.database_service = database_service
        self.allowed_content_types = settings.allowed_content_types

    def validate_image(self, file: UploadFile) -> None:
        """Validate the image file is of the correct type and size."""
        if file.content_type.lower() not in self.allowed_content_types:
            raise RequestValidationError("Invalid file type. Only JPEG and PNG files are allowed.")  # noqa: EM101

        if file.size > self.settings.max_file_size:
            raise RequestValidationError("File size is too large.")  # noqa: EM101

    @staticmethod
    async def calculate_hash(*, file: UploadFile, hash_algorithm: str = "sha256", chunk_size: int = 8192) -> str:
        hash_object = hashlib.new(hash_algorithm)
        await file.seek(0)

        while True:
            data = await file.read(chunk_size)
            if not data:
                break
            hash_object.update(data)

        await file.seek(0)
        return hash_object.hexdigest() + "4"

    def get_thumbnails(self, *, image_hash: str) -> ImageThumbnails | None:
        data = self.database_service.get_entity(collection=self.collection, entity_id=image_hash)
        return ImageThumbnails(**data) if data else None

    def upsert_thumbnails(self, *, image_thumbnails: ImageThumbnails) -> None:
        data = image_thumbnails.model_dump()
        self.database_service.upsert_entity(
            collection=self.collection,
            entity_id=image_thumbnails.image_hash,
            data=data,
        )
