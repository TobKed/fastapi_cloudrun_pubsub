from typing import Any

from fastapi import Depends
from google.cloud import storage

from src.config import Settings
from src.config import get_settings
from src.utils.logging import debug_log_function_call


class StorageService:
    _client: storage.Client | None = None

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.project = self.settings.cloud_storage_project_id or self.settings.google_project_id

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client(project=self.project)
        return self._client

    @debug_log_function_call
    def upload(self, bucket_name: str, blob_name: str, file: Any, content_type: str | None = None) -> str:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file, content_type=content_type)
        blob.make_public()
        return blob.public_url
