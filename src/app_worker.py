from fastapi import Depends
from fastapi import Request
from fastapi import status
from loguru import logger

from src.api.app import create_app
from src.schemas.pubsub import GooglePubSubPushRequestGenerateThumbnails
from src.services.image_service import ImageService

app = create_app()


@app.post("/generate_thumbnails", status_code=status.HTTP_204_NO_CONTENT)
async def generate_thumbnails(
    pubsub_request: GooglePubSubPushRequestGenerateThumbnails,
    image_service: ImageService = Depends(ImageService),
) -> None:
    logger.debug(f"Request from PubSub: {pubsub_request}")
    await image_service.process_thumbnails_worker_request(
        image_hash=pubsub_request.message.attributes.image_hash,
        image_url=pubsub_request.message.attributes.image_url,
    )


@app.post("/generate_thumbnails_dlq", status_code=status.HTTP_204_NO_CONTENT)
async def generate_thumbnails_dlq(request: Request) -> None:
    """Just log the request body for dead letter queue."""
    body = await request.body()
    logger.info(f"Request from PubSub DLQ: {body=}")
