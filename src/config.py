from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    title: str = "Fast API, CluudRun and PubSub"
    version: str = "0.0.1"

    google_project_id: str
    pubsub_main_topic: str

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "debug": self.debug,
            "title": self.title,
            "version": self.version,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
