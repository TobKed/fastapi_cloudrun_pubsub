from fastapi import Depends
from google.cloud import datastore

from src.config import Settings
from src.config import get_settings


class DatabaseService:
    _client: datastore.Client | None = None

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.project = self.settings.datastore_project_id or self.settings.google_project_id

    @property
    def client(self) -> datastore.Client:
        if self._client is None:
            self._client = datastore.Client(project=self.project)
        return self._client

    def get_entity(self, *, collection: str, entity_id: str) -> datastore.Entity | None:
        entity_key = self.client.key(collection, entity_id)
        return self.client.get(entity_key)

    def upsert_entity(self, *, collection: str, entity_id: str, data: dict) -> None:
        entity_key = self.client.key(collection, entity_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(data)
        self.client.put(entity)
