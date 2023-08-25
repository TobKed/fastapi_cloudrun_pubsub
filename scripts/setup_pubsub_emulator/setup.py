from pubsub import setup_pubsub_emulator

from config import get_settings

settings = get_settings()

if __name__ == "__main__":
    setup_pubsub_emulator(
        host=settings.pubsub_emulator_host,
        project_id=settings.pubsub_project_id,
        topic_id=settings.pubsub_generate_thumbnails,
        subscription_name=settings.pubsub_generate_thumbnails_subscription,
        subscription_name_dlq=settings.pubsub_generate_thumbnails_subscription_dlq,
        topic_id_dlq=settings.pubsub_generate_thumbnails_dlq,
        topic_push_endpoint=settings.pubsub_generate_thumbnails_push_endpoint,
        topic_push_endpoint_dlq=settings.pubsub_generate_thumbnails_push_endpoint_dlq,
    )
