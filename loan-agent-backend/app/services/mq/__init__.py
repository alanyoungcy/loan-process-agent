"""
Message Queue Service Module
"""

from app.services.mq.rabbitmq_client import (
    MessageQueueClient,
    get_mq_client,
    close_mq_client
)

__all__ = [
    "MessageQueueClient",
    "get_mq_client",
    "close_mq_client"
]
