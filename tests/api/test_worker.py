from fastapi import status
from httpx import AsyncClient


async def test_image_generation_dlq(client_worker: AsyncClient) -> None:
    response = await client_worker.post("/generate_annotations_dlq", json={"id": "foobar"})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""
