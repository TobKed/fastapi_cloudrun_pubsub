from fastapi import status
from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def healthcheck() -> None:
    pass
