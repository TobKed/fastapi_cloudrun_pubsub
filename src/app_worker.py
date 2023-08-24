from fastapi import FastAPI
from fastapi import status
from loguru import logger

from src.api import health
from src.api.handlers import register_error_handling
from src.config import get_settings
from src.schemas.pubsub import GooglePubSubPushRequest

settings = get_settings()
app = FastAPI(**settings.fastapi_kwargs)
app.include_router(health.router)
register_error_handling(app)


@app.post("/pubsub", status_code=status.HTTP_204_NO_CONTENT)
async def pubsub(pubsub_request: GooglePubSubPushRequest) -> None:
    logger.debug(f"Request from PubSub: {pubsub_request}")


@app.post("/pubsub_dlq", status_code=status.HTTP_204_NO_CONTENT)
async def pubsub_dlq(pubsub_request: GooglePubSubPushRequest) -> None:
    logger.debug(f"Request from PubSub DLQ: {pubsub_request}")
