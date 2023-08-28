from src.services.storage_service import StorageService
from tests.conftest import settings


async def test_storage_service_upload_image(gcp_storage_client) -> None:
    storage_service = StorageService(settings=settings)
    bucket_name = "test-bucket"
    blob_name = "test.jpeg"
    file = "image.io"
    content_type = "image/jpeg"

    storage_service.upload(
        bucket_name=bucket_name,
        blob_name=blob_name,
        file=file,  # type: ignore[arg-type]
        content_type=content_type,
    )

    bucket = gcp_storage_client.return_value.bucket
    blob = bucket.return_value.blob
    upload_from_file_method = blob.return_value.upload_from_file
    make_public_method = blob.return_value.make_public

    bucket.assert_called_once_with(bucket_name)
    blob.assert_called_once_with(blob_name)
    upload_from_file_method.assert_called_once_with(file, content_type=content_type)
    make_public_method.assert_called_once()
