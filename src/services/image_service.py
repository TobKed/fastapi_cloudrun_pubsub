import hashlib

from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import UploadFile
from fastapi import status
from fastapi.exceptions import RequestValidationError

from src.api.exceptions import ThumbnailGenerationError
from src.config import Settings
from src.config import get_settings
from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails
from src.services.database_service import DatabaseService
from src.services.queue_service import QueueService
from src.utils.logging import debug_log_function_call


class ImageService:
    collection = "ImageCollection"

    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        database_service: DatabaseService = Depends(DatabaseService),
        queue_service: QueueService = Depends(QueueService),
    ) -> None:
        self.settings = settings
        self.database_service = database_service
        self.queue_service = queue_service
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
    def process_thumbnails_worker_request(self, *, image_hash: str, image_url: str) -> None:
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

            thumbnails = self.generate_thumbnails(image_hash=image_hash, image_url=image_url)
            image_thumbnails = ImageThumbnails(
                image_hash=image_hash,
                image_url=image_url,
                thumbnails=thumbnails,
                status=ImageThumbnailsGenerationStatus.SUCCESS,
            )
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)
        except:  # noqa: E722
            image_thumbnails = ImageThumbnails(
                image_hash=image_hash,
                image_url=image_url,
                status=ImageThumbnailsGenerationStatus.ERROR,
            )
            self.upsert_thumbnails(image_thumbnails=image_thumbnails)

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
        await file.seek(0)
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
    def upload_image_to_storage(self, *, file: UploadFile, image_hash: str) -> str:
        # TODO
        return "https://static01.nyt.com/images/2021/09/14/science/07CAT-STRIPES/07CAT-STRIPES-mediumSquareAt3X-v2.jpg"

    @debug_log_function_call
    def send_to_worker(self, *, file: UploadFile, image_thumbnails: ImageThumbnails) -> None:
        """
        Upload the image to storage and send a message to the worker.
        Update the image_thumbnails status to `queued`.
        """
        image_thumbnails.image_url = self.upload_image_to_storage(file=file, image_hash=image_thumbnails.image_hash)

        self.queue_service.publish(
            message=image_thumbnails.image_hash,
            image_hash=image_thumbnails.image_hash,
            image_url=image_thumbnails.image_url,
        )

        image_thumbnails.status = ImageThumbnailsGenerationStatus.QUEUED
        self.upsert_thumbnails(image_thumbnails=image_thumbnails)

    @debug_log_function_call
    def generate_thumbnails(self, image_hash: str, image_url: str) -> list[str]:
        # TODO
        # generate thumbnails
        # upload thumbnails to storage
        return [
            "https://static01.nyt.com/images/2021/09/14/science/07CAT-STRIPES/07CAT-STRIPES-mediumSquareAt3X-v2.jpg",
            "https://static01.nyt.com/images/2021/09/14/science/07CAT-STRIPES/07CAT-STRIPES-mediumSquareAt3X-v2.jpg",
            "https://static01.nyt.com/images/2021/09/14/science/07CAT-STRIPES/07CAT-STRIPES-mediumSquareAt3X-v2.jpg",
        ]
