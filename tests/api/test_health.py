from fastapi import status
from httpx import AsyncClient


async def test_healthcheck_api(client_api: AsyncClient) -> None:
    response = await client_api.get("/health")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""


async def test_healthcheck_worker(client_worker: AsyncClient) -> None:
    response = await client_worker.get("/health")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""
