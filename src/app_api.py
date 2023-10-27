from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from loguru import logger

from src.api.app import create_app
from src.api.exceptions import AnnotationGenerationError
from src.enums.image import ImageAnnotationsGenerationStatus
from src.schemas.image import ImageClassification
from src.services.image_service import ImageService

app = create_app()


@app.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/what/status/{image_hash}")
async def get_image(
    image_hash: str,
    image_service: ImageService = Depends(ImageService),
) -> ImageClassification:
    """Returns image classification if it exists in the database."""
    image_classification = image_service.get_image_classification(image_hash=image_hash)

    if not image_classification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found {image_hash=}",
        )

    return image_classification


@app.post("/what/slow")
async def what_is_it_slow(
    img: UploadFile,
    image_service: ImageService = Depends(ImageService),
) -> ImageClassification:
    """Returns image classification if it exists in the database, otherwise generates it synchronously."""
    image_service.validate_image(file=img)
    image_hash = await image_service.calculate_hash(file=img)
    image_classification = image_service.get_image_classification(image_hash=image_hash)

    if image_classification:
        logger.info(f"Image Classification already in db: {image_classification=}")
        return image_classification

    logger.info(f"Image Classification not found in db: {image_classification=}")

    image_classification = ImageClassification(
        image_hash=image_hash,
        status=ImageAnnotationsGenerationStatus.PENDING,
    )

    try:
        image_classification.annotations = image_service.generate_annotations(contents=await img.read())
        image_classification.status = ImageAnnotationsGenerationStatus.SUCCESS
    except AnnotationGenerationError:
        image_classification.status = ImageAnnotationsGenerationStatus.ERROR
        logger.exception(
            f"Error generating annotations for Image Classification: {image_classification=}",
            exc_info=True,
        )

    image_service.upsert_image_classification(image_classification=image_classification)
    return image_classification


@app.post("/what/fast")
async def what_is_it_fast(
    img: UploadFile,
    background_tasks: BackgroundTasks,
    image_service: ImageService = Depends(ImageService),
) -> ImageClassification:
    """Returns image classification if it exists in the database, otherwise sends a request to the queue."""
    image_service.validate_image(file=img)
    image_hash = await image_service.calculate_hash(file=img)
    image_classification = image_service.get_image_classification(image_hash=image_hash)

    if image_classification:
        logger.info(f"Image Classification already in db: {image_classification=}")
        return image_classification

    logger.info(
        f"Image Classification not found in db, "
        f"sending annotation generation request to the queue: {image_classification=}",
    )

    image_classification = ImageClassification(
        image_hash=image_hash,
        status=ImageAnnotationsGenerationStatus.PENDING,
    )

    image_service.upsert_image_classification(image_classification=image_classification)
    background_tasks.add_task(
        image_service.send_generation_request_to_worker,
        file=img,
        image_classification=image_classification,
    )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=dict(image_classification))
