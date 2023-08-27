from unittest import mock

from src.services.database_service import DatabaseService
from tests.conftest import settings


async def test_database_get_entity(client, gcp_datastore_client) -> None:
    database_service = DatabaseService(settings=settings)
    collection = "CollectionName"
    entity_id = "entity-id"

    database_service.get_entity(collection=collection, entity_id=entity_id)

    key_method = gcp_datastore_client.return_value.key
    get_method = gcp_datastore_client.return_value.get

    key_method.assert_called_once_with(collection, entity_id)
    get_method.assert_called_once_with(key_method.return_value)


@mock.patch("google.cloud.datastore.Entity")
async def test_database_upsert_entity(entity_mock, client, gcp_datastore_client) -> None:
    database_service = DatabaseService(settings=settings)
    collection = "CollectionName"
    entity_id = "entity-id"
    data = {"key_1": "value_1", "key_2": "value_2"}

    database_service.upsert_entity(collection=collection, entity_id=entity_id, data=data)

    key_method = gcp_datastore_client.return_value.key
    put_method = gcp_datastore_client.return_value.put

    entity_mock.assert_called_with(key=key_method.return_value)
    entity_mock.return_value.update.assert_called_with(data)

    put_method.assert_called_with(entity_mock.return_value)
