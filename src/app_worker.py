from fastapi import Depends
from fastapi import Request
from fastapi import status
from loguru import logger

from src.api.app import create_app
from src.api.exceptions import ThumbnailGenerationError
from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails
from src.schemas.pubsub import GooglePubSubPushRequestGenerateThumbnails
from src.services.image_service import ImageService

app = create_app()


@app.post("/generate_thumbnails", status_code=status.HTTP_204_NO_CONTENT)
async def generate_thumbnails(
    pubsub_request: GooglePubSubPushRequestGenerateThumbnails,
    image_service: ImageService = Depends(ImageService),
) -> None:
    logger.debug(f"Request from PubSub: {pubsub_request}")

    image_hash = pubsub_request.message.attributes.image_hash
    image_url = pubsub_request.message.attributes.image_url

    try:
        image_thumbnails = image_service.get_thumbnails(image_hash=image_hash)
        if not image_thumbnails:
            msg = f"Image thumbnails does not exist. {image_hash=}"
            raise ThumbnailGenerationError(detail=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if image_thumbnails.status.is_done():
            logger.debug(f"Image thumbnails already processed: {image_thumbnails=}")
            return

        thumbnails = await image_service.generate_thumbnails(image_hash=image_hash, image_url=image_url)

        image_thumbnails = ImageThumbnails(
            image_hash=image_hash,
            image_url=image_url,
            thumbnails=thumbnails,
            status=ImageThumbnailsGenerationStatus.SUCCESS,
        )
        image_service.upsert_thumbnails(image_thumbnails=image_thumbnails)
    except ThumbnailGenerationError:
        logger.exception(f"Error generating thumbnails: {image_hash=}", exc_info=True)
        image_thumbnails = ImageThumbnails(
            image_hash=image_hash,
            image_url=image_url,
            status=ImageThumbnailsGenerationStatus.ERROR,
        )
        image_service.upsert_thumbnails(image_thumbnails=image_thumbnails)


@app.post("/generate_thumbnails_dlq", status_code=status.HTTP_204_NO_CONTENT)
async def generate_thumbnails_dlq(request: Request) -> None:
    """Just log the request body for dead letter queue."""
    body = await request.body()
    logger.info(f"Request from PubSub DLQ: {body=}")
