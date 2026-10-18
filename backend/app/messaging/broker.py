"""RabbitMQ access with per-service authentication (constitution ZT-5, T-123).

* The connection always uses TLS with the broker certificate verified against the local CA; there
  is no plain-AMQP option.
* Each service connects as its own broker user. The broker only lets that user publish with a
  matching `user_id`, so the `user_id` of a received message is the unforgeable name of the sender.
* `require_sender` is the consumer-side check: a message from any other sender is rejected.
"""

import ssl
import uuid
from collections.abc import Collection
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

from app.core.config import Settings


class UnauthorisedSender(Exception):
    """A message arrived from a sender that is not allowed to send it."""


def _settings(settings: Settings) -> tuple[str, str, str]:
    if not (settings.mq_host and settings.mq_user and settings.mq_password):
        raise RuntimeError(
            "message broker is not configured: set AUCOFF_MQ_HOST, AUCOFF_MQ_USER and "
            "AUCOFF_MQ_PASSWORD (each service has its own broker user)"
        )
    return settings.mq_host, settings.mq_user, settings.mq_password


async def connect(settings: Settings) -> AbstractRobustConnection:
    host, user, password = _settings(settings)
    context = ssl.create_default_context(cafile=settings.mq_ca_file)
    return await aio_pika.connect_robust(
        host=host,
        port=settings.mq_port,
        login=user,
        password=password,
        virtualhost=settings.mq_vhost,
        ssl=True,
        ssl_context=context,
    )


def build_message(body: bytes, *, sender: str, **properties: Any) -> aio_pika.Message:
    """A persistent message that names its sender; the broker rejects a false `user_id`."""
    return aio_pika.Message(
        body=body,
        user_id=sender,
        message_id=str(uuid.uuid4()),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        **properties,
    )


def require_sender(message: AbstractIncomingMessage, allowed: Collection[str]) -> str:
    sender = message.user_id
    if not sender or sender not in allowed:
        raise UnauthorisedSender("message from an unexpected or unnamed sender")
    return sender
