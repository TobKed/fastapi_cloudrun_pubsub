from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pubsub_emulator_host: str
    pubsub_project_id: str
    pubsub_main_topic: str
    pubsub_main_topic_subscription: str
    pubsub_main_topic_push_endpoint: str
    pubsub_main_topic_dlq: str
    pubsub_main_topic_subscription_dlq: str
    pubsub_main_topic_push_endpoint_dlq: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
