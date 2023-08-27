from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Final

import pytest
from httpx import AsyncClient

from src.api.app import create_app
from src.config import get_settings
from tests.fixtures import *  # noqa: F403

BASE_PATH: Final = Path(__file__).parent.parent

app = create_app()
settings = get_settings()


@pytest.fixture()
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="https://test") as c:
        yield c
