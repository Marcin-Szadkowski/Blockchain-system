import json
from logging import getLogger

import pika

from blockchain_system.tasks import (
    handle_block_mined,
    handle_mine_block,
    handle_show_chain,
)

BROKER_DSN = "amqp://user:password@172.17.0.2:5672/"

logger = getLogger(__name__)


SUBSCRIBER_TASKS_MAP = {
    "blockchain.command.mine": handle_mine_block,
    "blockchain.command.show_chain": handle_show_chain,
    "blockchain.event.block_mined": handle_block_mined,
}


# Define the callback function to handle incoming messages
def route_event(ch, method, properties, body):
    if not method.routing_key in SUBSCRIBER_TASKS_MAP:
        return
    logger.info(
        f"Received message: {json.loads(body)}. Routing key: {method.routing_key}"
    )
    SUBSCRIBER_TASKS_MAP[method.routing_key](payload=json.loads(body))


class Subscriber:
    # Create a connection to the RabbitMQ broker using the DSN
    def __init__(self) -> None:
        parameters = pika.URLParameters(BROKER_DSN)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare the direct exchange
        self.channel.exchange_declare(
            exchange="topic_blockchain", exchange_type="topic"
        )

        # Declare a queue and bind it to the exchange with a routing key
        self.queue_name = ""
        routing_key = "blockchain.#"
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.queue_bind(
            exchange="topic_blockchain", queue=self.queue_name, routing_key=routing_key
        )

    def start_consuming(self):
        # Set up the consumer to use the callback function
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=route_event, auto_ack=True
        )

        # Start consuming messages
        logger.info("Waiting for messages. To exit, press CTRL+C")
        self.channel.start_consuming()
