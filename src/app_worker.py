from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from google.api_core.exceptions import GoogleAPICallError
from loguru import logger

from src.api.app import create_app
from src.api.exceptions import AnnotationGenerationError
from src.enums.image import ImageAnnotationsGenerationStatus
from src.schemas.image import ImageClassification
from src.schemas.pubsub import GooglePubSubPushRequestImageClassification
from src.services.image_service import ImageService

app = create_app()


@app.post("/generate_annotations", status_code=status.HTTP_204_NO_CONTENT)
async def generate_annotations(
    pubsub_request: GooglePubSubPushRequestImageClassification,
    image_service: ImageService = Depends(ImageService),
) -> None:
    logger.debug(f"Request from PubSub: {pubsub_request}")

    image_hash = pubsub_request.message.attributes.image_hash
    image_url = pubsub_request.message.attributes.image_url

    try:
        image_classification = image_service.get_image_classification(image_hash=image_hash)
        if not image_classification:
            msg = f"Image Classification not found in db: {image_hash=}"
            logger.info(msg)
            raise AnnotationGenerationError(detail=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if image_classification.status.is_done():
            logger.info(f"Image Classification is already processed: {image_classification=}")
            return

        image_content = await image_service.get_image_content_from_url(url=image_url)
        annotations = image_service.generate_annotations(contents=image_content)

        image_classification = ImageClassification(
            image_hash=image_hash,
            image_url=image_url,
            annotations=annotations,
            status=ImageAnnotationsGenerationStatus.SUCCESS,
        )
        image_service.upsert_image_classification(image_classification=image_classification)
    except (HTTPException, GoogleAPICallError):
        logger.exception(f"Error generating annotations for Image Classification: {image_hash=}", exc_info=True)
        image_classification = ImageClassification(
            image_hash=image_hash,
            image_url=image_url,
            status=ImageAnnotationsGenerationStatus.ERROR,
        )
        image_service.upsert_image_classification(image_classification=image_classification)


@app.post("/generate_annotations_dlq", status_code=status.HTTP_204_NO_CONTENT)
async def generate_annotations_dlq(request: Request) -> None:
    """Just log the request body for dead letter queue."""
    body = await request.body()
    logger.info(f"Request from PubSub DLQ: {body=}")
