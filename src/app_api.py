from fastapi import Depends
from fastapi import FastAPI
from fastapi import UploadFile
from google.cloud import pubsub_v1
from loguru import logger

from src.api import health
from src.api.handlers import register_error_handling
from src.config import get_settings
from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails
from src.services.image_service import ImageService

settings = get_settings()
app = FastAPI(**settings.fastapi_kwargs)
app.include_router(health.router)
register_error_handling(app)


@app.get("/send")
async def send() -> dict:
    text = "test data"

    pubsub_publisher = pubsub_v1.PublisherClient()
    pubsub_topic_path = pubsub_publisher.topic_path(
        project=settings.google_project_id,
        topic=settings.pubsub_main_topic,
    )
    future = pubsub_publisher.publish(
        topic=pubsub_topic_path,
        data=text.encode(),
    )
    message_id = future.result()

    response = {"messageId": message_id}

    logger.debug(f"Message sent: {response}")
    return response


@app.post("/image/upload/")
async def upload_image(
    file: UploadFile,
    image_service: ImageService = Depends(ImageService),
) -> ImageThumbnails:
    image_service.validate_image(file)
    image_hash = await image_service.calculate_hash(file=file)
    image_thumbnails = image_service.get_thumbnails(image_hash=image_hash)
    if image_thumbnails and image_thumbnails.is_done():
        logger.debug(f"Thumbnails already exists: {image_thumbnails}")
        return image_thumbnails
    if image_thumbnails and image_thumbnails.is_queued():
        logger.debug(f"Thumbnails generation is queued: {image_thumbnails}")
        return image_thumbnails

    logger.debug(f"Image does not exist: {image_hash=}")
    image_thumbnails = ImageThumbnails(
        image_hash=image_hash,
        thumbnails=["22", "33"],
        status=ImageThumbnailsGenerationStatus.SUCCESS,
    )
    image_service.upsert_thumbnails(image_thumbnails=image_thumbnails)
    return image_thumbnails
