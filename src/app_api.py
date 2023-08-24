from fastapi import FastAPI
from google.cloud import pubsub_v1
from loguru import logger

from src.api import health
from src.api.handlers import register_error_handling
from src.config import get_settings

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
