from google.cloud import datastore


class DatabaseService:
    _client: datastore.Client | None = None

    @property
    def client(self) -> datastore.Client:
        if self._client is None:
            self._client = datastore.Client()
        return self._client

    def get_entity(self, *, collection: str, entity_id: str) -> datastore.Entity | None:
        entity_key = self.client.key(collection, entity_id)
        return self.client.get(entity_key)

    def upsert_entity(self, *, collection: str, entity_id: str, data: dict) -> None:
        entity_key = self.client.key(collection, entity_id)
        entity = datastore.Entity(key=entity_key)
        entity.update(data)
        self.client.put(entity)
