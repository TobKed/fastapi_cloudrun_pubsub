from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pubsub_emulator_host: str
    pubsub_project_id: str
    pubsub_generate_annotations_topic: str
    pubsub_generate_annotations_subscription: str
    pubsub_generate_annotations_push_endpoint: str
    pubsub_generate_annotations_topic_dlq: str
    pubsub_generate_annotations_subscription_dlq: str
    pubsub_generate_annotations_push_endpoint_dlq: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
