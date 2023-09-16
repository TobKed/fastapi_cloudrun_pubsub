import hashlib
import io
from typing import IO

import httpx
import torch
import torch.nn.functional
from fastapi import Depends
from fastapi import UploadFile
from fastapi.exceptions import RequestValidationError
from google.api_core.exceptions import GoogleAPICallError
from loguru import logger
from PIL import Image
from transformers import ViTForImageClassification
from transformers import ViTImageProcessor

from src.config import Settings
from src.config import get_settings
from src.enums.image import ImageAnnotationsGenerationStatus
from src.schemas.image import ImageAnnotation
from src.schemas.image import ImageClassification
from src.services.database_service import DatabaseService
from src.services.queue_service import QueueService
from src.services.storage_service import StorageService
from src.utils.helpers import get_extension_from_filename
from src.utils.logging import debug_log_function_call


class ImageService:
    collection = "ImageCollection"

    _ml_model_prop_name = "_ml_model"
    _ml_model: ViTForImageClassification | None = None

    _ml_processor_prop_name = "_ml_processor"
    _ml_processor: ViTImageProcessor | None = None

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

    def get_ml_processor(self) -> ViTImageProcessor:
        """Ugly class property hack to avoid loading the processor on every request."""
        if not self._ml_processor:
            logger.info("Loading ML processor")
            processor = ViTImageProcessor.from_pretrained(self.settings.ml_model_dir)
            setattr(
                ImageService,
                self._ml_processor_prop_name,
                processor,
            )
        return self._ml_processor

    def get_ml_model(self) -> ViTForImageClassification:
        """Ugly class property hack to avoid loading the model on every request."""
        if not self._ml_model:
            logger.info("Loading ML model")
            model = ViTForImageClassification.from_pretrained(self.settings.ml_model_dir)
            setattr(
                ImageService,
                self._ml_model_prop_name,
                model,
            )
        return self._ml_model

    def validate_image(self, file: UploadFile) -> None:
        """Validate the image file is of the correct type and size."""
        if file.content_type.lower() not in self.allowed_content_types:
            raise RequestValidationError("Invalid file type. Only JPEG and PNG files are allowed.")  # noqa: EM101

        if file.size > self.settings.max_file_size:
            raise RequestValidationError("File size is too large.")  # noqa: EM101

    @staticmethod
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

    def get_image_classification(self, *, image_hash: str) -> ImageClassification | None:
        data = self.database_service.get_entity(collection=self.collection, entity_id=image_hash)
        return ImageClassification(**data) if data else None

    def upsert_image_classification(self, *, image_classification: ImageClassification) -> None:
        data = image_classification.model_dump()
        self.database_service.upsert_entity(
            collection=self.collection,
            entity_id=image_classification.image_hash,
            data=data,
        )
        self.database_service.get_entity(collection=self.collection, entity_id=image_classification.image_hash)

    async def upload_to_storage(self, *, file: IO, blob_name: str, content_type: str | None = None) -> str:
        return self.storage_service.upload(
            bucket_name=self.settings.cloud_storage_bucket,
            blob_name=blob_name,
            file=file,
            content_type=content_type,
        )

    @debug_log_function_call
    async def send_generation_request_to_worker(
        self,
        *,
        file: UploadFile,
        image_classification: ImageClassification,
    ) -> None:
        """
        Upload the image to storage and send a message to the worker.
        Update the image_classification status to `queued`.
        """
        blob_name = f"{image_classification.image_hash}{get_extension_from_filename(file.filename)}"
        try:
            image_classification.image_url = await self.upload_to_storage(
                file=file.file,
                blob_name=blob_name,
                content_type=file.content_type,
            )

            self.queue_service.publish(
                message=image_classification.image_hash,
                image_hash=image_classification.image_hash,
                image_url=image_classification.image_url,
            )

            image_classification.status = ImageAnnotationsGenerationStatus.QUEUED
            self.upsert_image_classification(image_classification=image_classification)
        except GoogleAPICallError:
            image_classification.status = ImageAnnotationsGenerationStatus.ERROR
            logger.exception(
                f"Error generating annotations for Image Classification: {image_classification=}",
                exc_info=True,
            )

    def generate_annotations(self, contents: bytes) -> list[ImageAnnotation]:
        processor = self.get_ml_processor()
        model = self.get_ml_model()

        image = Image.open(io.BytesIO(contents))
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        top_annotations = torch.topk(probabilities, self.settings.num_annotations, dim=1)

        annotations = []
        for i in range(self.settings.num_annotations):
            label_index = top_annotations.indices[0][i].item()
            confidence = top_annotations.values[0][i].item()
            label = model.config.id2label[label_index]
            annotations.append(ImageAnnotation(index=i + 1, label=label, confidence=f"{confidence:.2f}"))

        return annotations

    @staticmethod
    async def get_image_content_from_url(url: str) -> bytes:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.content
