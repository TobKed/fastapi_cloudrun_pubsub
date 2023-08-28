from src.services.queue_service import QueueService
from tests.conftest import settings


async def test_storage_service_upload_image(gcp_pubsub_client) -> None:
    queue_service = QueueService(settings=settings)
    message = "test message"
    attrs = {"attr_1": "test attr 1", "attr_2": "test attr 2"}

    queue_service.publish(message=message, **attrs)

    topic_path_method = gcp_pubsub_client.return_value.topic_path
    publish_method = gcp_pubsub_client.return_value.publish

    publish_method.assert_called_once_with(
        topic=topic_path_method.return_value,
        data=message.encode(),
        **attrs,
    )
