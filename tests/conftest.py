from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Final

import pytest
from httpx import AsyncClient

from src.app_api import app as app_api
from src.app_worker import app as app_worker
from src.config import get_settings
from tests.fixtures import *  # noqa: F403

BASE_PATH: Final = Path(__file__).parent.parent


settings = get_settings()


@pytest.fixture()
async def client_api() -> AsyncGenerator:
    async with AsyncClient(app=app_api, base_url="https://test") as c:
        yield c


@pytest.fixture()
async def client_worker() -> AsyncGenerator:
    async with AsyncClient(app=app_worker, base_url="https://test") as c:
        yield c
