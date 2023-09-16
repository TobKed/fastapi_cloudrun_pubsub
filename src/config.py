from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).absolute().parent.parent
MODEL_DIR = str(ROOT_DIR / "ml_models/google/vit-base-patch16-224")


class Settings(BaseSettings):
    debug: bool = False
    title: str = "FastAPI, CluudRun and PubSub"
    version: str = "0.0.1"

    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_content_types: tuple[str, ...] = ("image/jpeg", "image/png")

    google_project_id: str
    pubsub_project_id: str | None = None
    datastore_project_id: str | None = None
    cloud_storage_project_id: str | None = None

    pubsub_generate_annotations_topic: str
    cloud_storage_bucket: str
    datastore_database: str | None = None

    ml_model_dir: str = MODEL_DIR
    num_annotations: int = 5  # Number of top annotations to display

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
