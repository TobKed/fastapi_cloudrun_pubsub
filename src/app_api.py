from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from src.api.app import create_app
from src.schemas.image import ImageThumbnails
from src.services.image_service import ImageService

app = create_app()


@app.post("/image/upload/")
async def upload_image(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    image_service: ImageService = Depends(ImageService),
) -> ImageThumbnails:
    return await image_service.process_thumbnails_upload_request(
        file=file,
        background_tasks=background_tasks,
    )


@app.get("/image/{image_hash}/")
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
