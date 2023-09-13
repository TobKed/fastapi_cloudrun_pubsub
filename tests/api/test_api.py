from fastapi import status
from httpx import AsyncClient


class TestGetImageGenerationStatusEndpoint:
    url = "/what/status"

    async def test_raises_for_missing_image(self, client_api: AsyncClient) -> None:
        response = await client_api.get(self.url + "/foo")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Image not found image_hash='foo'"
