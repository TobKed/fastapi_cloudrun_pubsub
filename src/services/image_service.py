import hashlib
from tempfile import SpooledTemporaryFile
from typing import IO

import httpx
from fastapi import Depends
from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from google.api_core.exceptions import GoogleAPICallError
from loguru import logger
from PIL import Image

from src.config import Settings
from src.config import get_settings
from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails
from src.services.database_service import DatabaseService
from src.services.queue_service import QueueService
from src.services.storage_service import StorageService
from src.utils.helpers import get_extension_from_filename
from src.utils.helpers import get_format_from_content_type
from src.utils.logging import debug_log_function_call


class ImageService:
    collection = "ImageCollection"

    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        database_service: DatabaseService = Depends(DatabaseService),
        queue_service: QueueService = Depends(QueueService),
        storage_service: StorageService = Depends(StorageService),
    ) -> None:
        self.settings = settings
        self.database_service = database_service
        self.queue_service = queue_service
        self.storage_service = storage_service
        self.allowed_content_types = settings.allowed_content_types

    @debug_log_function_call
    def validate_image(self, file: UploadFile) -> None:
        """Validate the image file is of the correct type and size."""
        if file.content_type.lower() not in self.allowed_content_types:
            raise RequestValidationError("Invalid file type. Only JPEG and PNG files are allowed.")  # noqa: EM101

        if file.size > self.settings.max_file_size:
            raise RequestValidationError("File size is too large.")  # noqa: EM101

    @staticmethod
    @debug_log_function_call
    async def calculate_hash(*, file: UploadFile) -> str:
        """Calculate the sha256 hash of the file."""
        hash_object = hashlib.sha256()
        chunk_size: int = 8192

        while True:
            data = await file.read(chunk_size)
            if not data:
                break
            hash_object.update(data)

        await file.seek(0)
        return hash_object.hexdigest()

    @debug_log_function_call
    def get_thumbnails(self, *, image_hash: str) -> ImageThumbnails | None:
        data = self.database_service.get_entity(collection=self.collection, entity_id=image_hash)
        return ImageThumbnails(**data) if data else None

    @debug_log_function_call
    def upsert_thumbnails(self, *, image_thumbnails: ImageThumbnails) -> None:
        data = image_thumbnails.model_dump()
        self.database_service.upsert_entity(
            collection=self.collection,
            entity_id=image_thumbnails.image_hash,
            data=data,
        )
        self.database_service.get_entity(collection=self.collection, entity_id=image_thumbnails.image_hash)

    @debug_log_function_call
    async def upload_to_storage(self, *, file: IO, blob_name: str, content_type: str | None = None) -> str:
        return self.storage_service.upload(
            bucket_name=self.settings.cloud_storage_bucket,
            blob_name=blob_name,
            file=file,
            content_type=content_type,
        )

    @debug_log_function_call
    async def send_generation_request_to_worker(self, *, file: UploadFile, image_thumbnails: ImageThumbnails) -> None:
        """
        Upload the image to storage and send a message to the worker.
        Update the image_thumbnails status to `queued`.
        """
        blob_name = f"{image_thumbnails.image_hash}{get_extension_from_filename(file.filename)}"
        try:
            image_thumbnails.image_url = await self.upload_to_storage(
                file=file.file,
                blob_name=blob_name,
                content_type=file.content_type,
            )

            self.queue_service.publish(
                message=image_thumbnails.image_hash,
                image_hash=image_thumbnails.image_hash,
                image_url=image_thumbnails.image_url,
            )

            image_thumbnails.status = ImageThumbnailsGenerationStatus.QUEUED
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)
        except GoogleAPICallError:
            image_thumbnails.status = ImageThumbnailsGenerationStatus.ERROR
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)
            logger.exception(f"Error generating thumbnails: {image_thumbnails=}", exc_info=True)

    @debug_log_function_call
    async def generate_thumbnails(self, *, image_hash: str, image_url: str) -> list[str]:
        """
        Generate thumbnails for the image.
        Return a list of thumbnail urls.
        """
        thumbnails = []
        async with httpx.AsyncClient() as client:
            r = await client.get(image_url)
            r.raise_for_status()
            image_content = r.content
            image_content_type = r.headers.get("content-type")
            thumbnail_format = get_format_from_content_type(image_content_type)

        for thumbnail_size in self.settings.thumbnail_sizes:
            with (
                SpooledTemporaryFile() as tmp_source_file,
                SpooledTemporaryFile() as tmp_thumbnail_file,
            ):
                tmp_source_file.write(image_content)
                self._generate_thumbnail(
                    source_file_obj=tmp_source_file,
                    thumbnail_file_obj=tmp_thumbnail_file,
                    thumbnail_format=thumbnail_format,
                    thumbnail_size=thumbnail_size,
                )

                thumbnail_blob_name = f"{image_hash}-{thumbnail_size[0]}x{thumbnail_size[1]}.{thumbnail_format}"
                thumbnail_url = await self.upload_to_storage(
                    file=tmp_thumbnail_file,
                    blob_name=thumbnail_blob_name,
                    content_type=image_content_type,
                )

                thumbnails.append(thumbnail_url)

        return thumbnails

    @staticmethod
    def _generate_thumbnail(
        *,
        thumbnail_format: str | None,
        thumbnail_size: tuple[int, int],
        source_file_obj: IO,
        thumbnail_file_obj: IO,
    ) -> None:
        image = Image.open(source_file_obj)
        image.thumbnail(thumbnail_size)
        image.save(thumbnail_file_obj, format=thumbnail_format)
        thumbnail_file_obj.seek(0)
