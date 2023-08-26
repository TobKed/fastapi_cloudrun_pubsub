from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Final

import pytest
from httpx import AsyncClient

from src.api.app import create_app

BASE_PATH: Final = Path(__file__).parent.parent

app = create_app()


@pytest.fixture()
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="https://test") as c:
        yield c
