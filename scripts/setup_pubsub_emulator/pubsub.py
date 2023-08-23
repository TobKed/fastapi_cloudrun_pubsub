import grpc
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import AlreadyExists
from google.auth.credentials import AnonymousCredentials
from google.pubsub_v1 import DeadLetterPolicy
from google.pubsub_v1 import GetSubscriptionRequest
from google.pubsub_v1 import GetTopicRequest
from google.pubsub_v1 import PushConfig
from google.pubsub_v1.services.publisher.client import PublisherClient
from google.pubsub_v1.services.publisher.transports.grpc import PublisherGrpcTransport
from google.pubsub_v1.services.subscriber.client import SubscriberClient
from google.pubsub_v1.services.subscriber.transports import SubscriberGrpcTransport
from google.pubsub_v1.types import Subscription
from google.pubsub_v1.types import Topic
from loguru import logger


def get_publisher_client(endpoint: str) -> PublisherClient:
    grpc_channel = grpc.insecure_channel(endpoint)
    transport = PublisherGrpcTransport(channel=grpc_channel, credentials=AnonymousCredentials())
    client_options = ClientOptions(api_endpoint=endpoint)
    return PublisherClient(transport=transport, client_options=client_options)


def get_subscriber_client(endpoint: str) -> SubscriberClient:
    grpc_channel = grpc.insecure_channel(endpoint)
    transport = SubscriberGrpcTransport(channel=grpc_channel, credentials=AnonymousCredentials())
    client_options = ClientOptions(api_endpoint=endpoint)
    return SubscriberClient(transport=transport, client_options=client_options)


def get_topic_path(client: PublisherClient, project_id: str, topic_name: str) -> str:
    return client.topic_path(project_id, topic_name)


def get_topic(client: PublisherClient, topic_path: str) -> Topic:
    request = GetTopicRequest(topic=topic_path)
    return client.get_topic(request)


def create_topic(client: PublisherClient, topic_path: str) -> Topic:
    logger.info(f"Creating topic {topic_path} ...")

    request = Topic(name=topic_path)

    try:
        topic = client.create_topic(request)
    except AlreadyExists:
        logger.info(f"Topic {topic_path} exists, retrieving ...")
        return get_topic(client, topic_path)
    else:
        logger.info(f"Created topic {topic.name}")
        logger.debug(f"Created topic details\n{topic}")


def get_subscription_path(client: SubscriberClient, project_id: str, subscription_name: str) -> str:
    return client.subscription_path(project_id, subscription_name)


def create_subscription(  # noqa: PLR0913
    client: SubscriberClient,
    topic_path: str,
    subscription_path: str,
    push_endpoint: str,
    dead_letter_topic: str | None = None,
    max_delivery_attempts: int = 5,
) -> Subscription:
    logger.info(f"Creating subscription {subscription_path} ...")

    push_config = PushConfig(push_endpoint=push_endpoint) if push_endpoint else None

    dead_letter_policy = (
        DeadLetterPolicy(dead_letter_topic=dead_letter_topic, max_delivery_attempts=max_delivery_attempts)
        if dead_letter_topic
        else None
    )

    request = Subscription(
        name=subscription_path,
        topic=topic_path,
        dead_letter_policy=dead_letter_policy,
        push_config=push_config,
    )

    try:
        subscription = client.create_subscription(request)
    except AlreadyExists:
        logger.info(f"Subscription {subscription_path} exists, retrieving ...")
        return get_subscription(client, subscription_path)
    else:
        logger.info(f"Created subscription {subscription.name}")
        logger.debug(f"Created subscription details:\n{subscription}")


def get_subscription(client: SubscriberClient, subscription_path: str) -> Subscription:
    request = GetSubscriptionRequest(subscription=subscription_path)
    return client.get_subscription(request)


def setup_pubsub_emulator(  # noqa: PLR0913
    host: str,
    project_id: str,
    topic_id: str,
    topic_id_dlq: str,
    subscription_name: str,
    subscription_name_dlq: str,
    topic_push_endpoint: str,
    topic_push_endpoint_dlq: str,
    max_delivery_attempts: int = 5,
) -> None:
    logger.info("Setting up Pub/Sub emulator ...")

    publisher_client = get_publisher_client(host)
    subscriber_client = get_subscriber_client(host)

    topic_path = get_topic_path(publisher_client, project_id, topic_id)
    create_topic(publisher_client, topic_path)

    dlq_topic_path = get_topic_path(publisher_client, project_id, topic_id_dlq)
    create_topic(publisher_client, dlq_topic_path)

    subscription_path = get_subscription_path(
        subscriber_client,
        project_id,
        subscription_name,
    )
    create_subscription(
        subscriber_client,
        topic_path=topic_path,
        subscription_path=subscription_path,
        push_endpoint=topic_push_endpoint,
        dead_letter_topic=dlq_topic_path,
        max_delivery_attempts=max_delivery_attempts,
    )

    dlq_subscription_path = get_subscription_path(
        subscriber_client,
        project_id,
        subscription_name_dlq,
    )
    create_subscription(
        subscriber_client,
        topic_path=dlq_topic_path,
        subscription_path=dlq_subscription_path,
        push_endpoint=topic_push_endpoint_dlq,
    )

    logger.info("Pub/Sub emulator setup complete!")
