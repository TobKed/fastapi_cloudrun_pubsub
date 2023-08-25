import hashlib
from tempfile import SpooledTemporaryFile
from typing import Any

import httpx
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import UploadFile
from fastapi import status
from fastapi.exceptions import RequestValidationError
from PIL import Image

from src.api.exceptions import ThumbnailGenerationError
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
    async def process_thumbnails_upload_request(
        self,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> ImageThumbnails:
        self.validate_image(file)
        image_hash = await self.calculate_hash(file=file)
        image_thumbnails = self.get_thumbnails(image_hash=image_hash)

        if image_thumbnails and image_thumbnails.status.is_not_pending():
            return image_thumbnails

        image_thumbnails = ImageThumbnails(
            image_hash=image_hash,
            status=ImageThumbnailsGenerationStatus.PENDING,
        )
        self.upsert_thumbnails(image_thumbnails=image_thumbnails)
        background_tasks.add_task(
            self.send_to_worker,
            file=file,
            image_thumbnails=image_thumbnails,
        )
        return image_thumbnails

    @debug_log_function_call
    async def process_thumbnails_worker_request(self, *, image_hash: str, image_url: str) -> None:
        try:
            image_thumbnails = self.get_thumbnails(image_hash=image_hash)
            if not image_thumbnails:
                msg = f"Image thumbnails does not exist. {image_hash=}"
                raise ThumbnailGenerationError(detail=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if image_thumbnails.thumbnails:
                msg = f"Image thumbnails does not contain thumbnails. {image_thumbnails=}"
                raise ThumbnailGenerationError(detail=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if image_thumbnails.status.is_done():
                return

            thumbnails = await self.generate_thumbnails(image_hash=image_hash, image_url=image_url)
            image_thumbnails = ImageThumbnails(
                image_hash=image_hash,
                image_url=image_url,
                thumbnails=thumbnails,
                status=ImageThumbnailsGenerationStatus.SUCCESS,
            )
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)
        except:
            image_thumbnails = ImageThumbnails(
                image_hash=image_hash,
                image_url=image_url,
                status=ImageThumbnailsGenerationStatus.ERROR,
            )
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)
            raise

    @debug_log_function_call
    def validate_image(self, file: UploadFile) -> None:
        """Validate the image file is of the correct type and size."""
        if file.content_type.lower() not in self.allowed_content_types:
            raise RequestValidationError("Invalid file type. Only JPEG and PNG files are allowed.")  # noqa: EM101

        if file.size > self.settings.max_file_size:
            raise RequestValidationError("File size is too large.")  # noqa: EM101

    @staticmethod
    @debug_log_function_call
    async def calculate_hash(*, file: UploadFile, hash_algorithm: str = "sha256", chunk_size: int = 8192) -> str:
        hash_object = hashlib.new(hash_algorithm)
        while True:
            data = await file.read(chunk_size)
            if not data:
                break
            hash_object.update(data)

        await file.seek(0)
        return hash_object.hexdigest() + "3333"

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
    async def upload_image_to_storage(self, *, file: Any, blob_name: str, content_type: str | None = None) -> str:
        return self.storage_service.upload(
            bucket_name=self.settings.cloud_storage_bucket,
            blob_name=blob_name,
            file=file,
            content_type=content_type,
        )

    @debug_log_function_call
    async def send_to_worker(self, *, file: UploadFile, image_thumbnails: ImageThumbnails) -> None:
        """
        Upload the image to storage and send a message to the worker.
        Update the image_thumbnails status to `queued`.
        """
        blob_name = f"{image_thumbnails.image_hash}{get_extension_from_filename(file.filename)}"
        image_thumbnails.image_url = await self.upload_image_to_storage(
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

    @debug_log_function_call
    async def generate_thumbnails(self, image_hash: str, image_url: str) -> list[str]:
        thumbnails = []
        async with httpx.AsyncClient() as client:
            r = await client.get(image_url)
            r.raise_for_status()
            content_type = r.headers.get("content-type")
            thumbnail_format = get_format_from_content_type(content_type)

            for thumbnail_size in self.settings.thumbnail_sizes:
                with (
                    SpooledTemporaryFile() as tmp_source_file,
                    SpooledTemporaryFile() as tmp_thumbnail_file,
                ):
                    thumbnail_blob_name = f"{image_hash}-{thumbnail_size[0]}x{thumbnail_size[1]}.{thumbnail_format}"

                    tmp_source_file.write(r.content)
                    image = Image.open(tmp_source_file)
                    image.thumbnail(thumbnail_size)
                    image.save(tmp_thumbnail_file, format=thumbnail_format)
                    tmp_thumbnail_file.seek(0)

                    thumbnail_url = await self.upload_image_to_storage(
                        file=tmp_thumbnail_file,
                        blob_name=thumbnail_blob_name,
                        content_type=content_type,
                    )

                    thumbnails.append(thumbnail_url)

        return thumbnails
