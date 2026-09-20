"""
RabbitMQ Message Queue Client
Handles async task publishing and consumption
"""

import json
import logging
import asyncio
from typing import Any, Callable, Optional, Dict
from datetime import datetime
import uuid

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType

from app.core.config import settings

logger = logging.getLogger(__name__)


class MessageQueueClient:
    """
    RabbitMQ client for async task processing
    Handles message publishing, consumption, and queue management
    """

    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.RABBITMQ_URL
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self._exchanges: Dict[str, aio_pika.Exchange] = {}

    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                self.url,
                timeout=30,
                client_properties={
                    "connection_name": "loan-agent-backend"
                }
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            logger.info(f"Connected to RabbitMQ at {self.url}")

            # Declare exchanges
            await self._declare_exchanges()
            # Declare queues
            await self._declare_queues()

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def _declare_exchanges(self):
        """Declare all exchanges"""
        exchanges = {
            "genai.tasks": ExchangeType.DIRECT,
            "genai.results": ExchangeType.TOPIC,
            "drools.validation": ExchangeType.DIRECT,
            "notifications": ExchangeType.FANOUT,
        }

        for name, exchange_type in exchanges.items():
            exchange = await self.channel.declare_exchange(
                name=name,
                type=exchange_type,
                durable=True
            )
            self._exchanges[name] = exchange
            logger.info(f"Declared exchange: {name} ({exchange_type.value})")

    async def _declare_queues(self):
        """Declare all queues with DLX support"""
        # Declare dead letter exchange
        dlx = await self.channel.declare_exchange(
            name="dlx",
            type=ExchangeType.TOPIC,
            durable=True
        )

        queues = [
            "genai.summarize",
            "genai.script_generation",
            "genai.rule_generation",
            "genai.batch_processing",
            "genai.intent_analysis",
            "drools.compliance_check",
            "notifications.email",
            "notifications.sms",
        ]

        for queue_name in queues:
            # Main queue with DLX
            queue = await self.channel.declare_queue(
                name=queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "dlx",
                    "x-dead-letter-routing-key": f"{queue_name}.failed",
                    "x-message-ttl": 300000,  # 5 min timeout
                    "x-max-priority": 10
                }
            )

            # Dead letter queue
            dlq = await self.channel.declare_queue(
                name=f"{queue_name}.failed",
                durable=True
            )

            # Bind DLQ to DLX
            await dlq.bind(dlx, routing_key=f"{queue_name}.failed")

            logger.info(f"Declared queue: {queue_name} with DLQ")

    async def publish_task(
        self,
        queue_name: str,
        task_data: Dict[str, Any],
        priority: int = 5,
        expiration: Optional[int] = None
    ) -> str:
        """
        Publish task to queue

        Args:
            queue_name: Queue name
            task_data: Task payload
            priority: Message priority (0-10)
            expiration: Message expiration in milliseconds

        Returns:
            Task ID
        """
        if not self.channel:
            await self.connect()

        task_id = str(uuid.uuid4())

        message_body = {
            "task_id": task_id,
            "payload": task_data,
            "priority": priority,
            "submitted_at": datetime.utcnow().isoformat(),
            "retry_count": 0
        }

        message = Message(
            body=json.dumps(message_body).encode(),
            priority=priority,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=task_id,
            timestamp=datetime.utcnow(),
            expiration=str(expiration) if expiration else None
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=queue_name
        )

        logger.info(f"Published task {task_id} to queue {queue_name}")

        return task_id

    async def consume_tasks(
        self,
        queue_name: str,
        handler: Callable,
        prefetch_count: int = 10
    ):
        """
        Consume tasks from queue

        Args:
            queue_name: Queue name
            handler: Async handler function
            prefetch_count: Number of messages to prefetch
        """
        if not self.channel:
            await self.connect()

        await self.channel.set_qos(prefetch_count=prefetch_count)

        queue = await self.channel.get_queue(queue_name)

        logger.info(f"Starting to consume from queue: {queue_name}")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=False):
                    try:
                        task_data = json.loads(message.body.decode())
                        task_id = task_data["task_id"]

                        logger.info(f"Processing task {task_id} from {queue_name}")

                        # Execute handler
                        result = await handler(task_data)

                        # Publish result
                        await self.publish_result(
                            task_id=task_id,
                            result=result,
                            status="completed"
                        )

                        logger.info(f"Completed task {task_id}")

                    except Exception as e:
                        logger.error(
                            f"Error processing message from {queue_name}: {str(e)}",
                            exc_info=True
                        )

                        # Publish failure result
                        task_id = task_data.get("task_id", "unknown")
                        await self.publish_result(
                            task_id=task_id,
                            result={"error": str(e)},
                            status="failed"
                        )

    async def publish_result(
        self,
        task_id: str,
        result: Any,
        status: str
    ):
        """
        Publish task result to results exchange

        Args:
            task_id: Task ID
            result: Task result data
            status: Task status (completed, failed)
        """
        if not self.channel:
            await self.connect()

        exchange = self._exchanges.get("genai.results")
        if not exchange:
            logger.error("Results exchange not found")
            return

        message_body = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "completed_at": datetime.utcnow().isoformat()
        }

        message = Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json"
        )

        await exchange.publish(
            message,
            routing_key=f"result.{status}"
        )

        logger.info(f"Published result for task {task_id}: {status}")

    async def publish_notification(
        self,
        notification_type: str,
        notification_data: Dict[str, Any]
    ):
        """
        Publish notification to fanout exchange

        Args:
            notification_type: Type of notification (email, sms)
            notification_data: Notification payload
        """
        if not self.channel:
            await self.connect()

        exchange = self._exchanges.get("notifications")
        if not exchange:
            logger.error("Notifications exchange not found")
            return

        message_body = {
            "notification_id": str(uuid.uuid4()),
            "type": notification_type,
            "data": notification_data,
            "created_at": datetime.utcnow().isoformat()
        }

        message = Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json"
        )

        await exchange.publish(message, routing_key="")

        logger.info(f"Published {notification_type} notification")

    async def get_queue_stats(self, queue_name: str) -> Dict[str, int]:
        """
        Get queue statistics

        Args:
            queue_name: Queue name

        Returns:
            Dict with message_count and consumer_count
        """
        if not self.channel:
            await self.connect()

        queue = await self.channel.get_queue(queue_name)
        declaration = await queue.declare(passive=True)

        return {
            "message_count": declaration.message_count,
            "consumer_count": declaration.consumer_count
        }

    async def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue

        Args:
            queue_name: Queue name

        Returns:
            Number of messages deleted
        """
        if not self.channel:
            await self.connect()

        queue = await self.channel.get_queue(queue_name)
        deleted = await queue.purge()

        logger.info(f"Purged {deleted} messages from {queue_name}")

        return deleted

    async def close(self):
        """Close connection to RabbitMQ"""
        if self.connection:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")


# Singleton instance
_mq_client: Optional[MessageQueueClient] = None


async def get_mq_client() -> MessageQueueClient:
    """Get or create MessageQueueClient singleton"""
    global _mq_client

    if _mq_client is None:
        _mq_client = MessageQueueClient()
        await _mq_client.connect()

    return _mq_client


async def close_mq_client():
    """Close MQ client connection"""
    global _mq_client

    if _mq_client:
        await _mq_client.close()
        _mq_client = None
