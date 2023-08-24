from pubsub import setup_pubsub_emulator

from config import get_settings

settings = get_settings()

if __name__ == "__main__":
    setup_pubsub_emulator(
        host=settings.pubsub_emulator_host,
        project_id=settings.pubsub_project_id,
        topic_id=settings.pubsub_main_topic,
        subscription_name=settings.pubsub_main_topic_subscription,
        subscription_name_dlq=settings.pubsub_main_topic_subscription_dlq,
        topic_id_dlq=settings.pubsub_main_topic_dlq,
        topic_push_endpoint=settings.pubsub_main_topic_push_endpoint,
        topic_push_endpoint_dlq=settings.pubsub_main_topic_push_endpoint_dlq,
    )
