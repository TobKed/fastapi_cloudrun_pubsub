from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from src.api.app import create_app
from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails
from src.services.image_service import ImageService

app = create_app()


@app.post("/image/upload/")
async def upload_image(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    image_service: ImageService = Depends(ImageService),
) -> ImageThumbnails:
    image_service.validate_image(file)
    image_hash = await image_service.calculate_hash(file=file)
    image_thumbnails = image_service.get_thumbnails(image_hash=image_hash)

    if image_thumbnails:
        return image_thumbnails

    image_thumbnails = ImageThumbnails(
        image_hash=image_hash,
        status=ImageThumbnailsGenerationStatus.PENDING,
    )
    image_service.upsert_thumbnails(image_thumbnails=image_thumbnails)
    background_tasks.add_task(
        image_service.send_generation_request_to_worker,
        file=file,
        image_thumbnails=image_thumbnails,
    )
    return image_thumbnails


@app.get("/image/status/{image_hash}")
async def get_image(
    image_hash: str,
    image_service: ImageService = Depends(ImageService),
) -> ImageThumbnails:
    image_thumbnails = image_service.get_thumbnails(image_hash=image_hash)

    if not image_thumbnails:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found {image_hash=}",
        )

    return image_thumbnails
