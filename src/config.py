from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    title: str = "Fast API, CluudRun and PubSub"
    version: str = "0.0.1"

    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_content_types: tuple[str, ...] = ("image/jpeg", "image/png")
    thumbnail_sizes: tuple[tuple[int, int], ...] = ((500, 500), (300, 300), (150, 150))

    google_project_id: str
    pubsub_project_id: str | None = None
    datastore_project_id: str | None = None
    cloud_storage_project_id: str | None = None

    pubsub_generate_thumbnails_topic: str
    cloud_storage_bucket: str

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
