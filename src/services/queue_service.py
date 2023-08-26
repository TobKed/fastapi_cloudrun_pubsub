from fastapi import Depends
from google.cloud import pubsub_v1
from loguru import logger

from src.config import Settings
from src.config import get_settings
from src.utils.logging import debug_log_function_call


class QueueService:
    _publisher_client: pubsub_v1.PublisherClient | None = None

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.topic = self.settings.pubsub_generate_thumbnails_topic
        self.project = self.settings.pubsub_project_id or self.settings.google_project_id

    @property
    def publisher_client(self) -> pubsub_v1.PublisherClient:
        if self._publisher_client is None:
            self._publisher_client = pubsub_v1.PublisherClient()
        return self._publisher_client

    @debug_log_function_call
    def publish(self, *, message: str = "", **attrs) -> str:
        """
        Publish a single message.
        Return the message ID or raise an exception.
        """
        logger.debug(f"Publishing message: `{message=}`, `{attrs=}`")

        pubsub_topic_path = self.publisher_client.topic_path(
            project=self.project,
            topic=self.topic,
        )
        future = self.publisher_client.publish(
            topic=pubsub_topic_path,
            data=message.encode(),
            **attrs,
        )
        return future.result()
