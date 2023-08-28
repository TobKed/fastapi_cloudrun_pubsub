from collections.abc import Generator
from unittest import mock

import pytest


@pytest.fixture()
def gcp_storage_client(autouse=True) -> Generator:
    with mock.patch("google.cloud.storage.Client") as client:
        yield client


@pytest.fixture()
def gcp_pubsub_client() -> Generator:
    with mock.patch("google.cloud.pubsub_v1.PublisherClient") as client:
        yield client


@pytest.fixture()
def gcp_datastore_client() -> Generator:
    with mock.patch("google.cloud.datastore.Client") as client:
        yield client
