import json
import time

import pika

from blockchain_system.blockchain import Block, Record

BROKER_DSN = "amqp://user:password@172.17.0.2:5672/"


class Publisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.broker_dsn = BROKER_DSN

    def connect(self):
        # Create a connection to the RabbitMQ broker using the DSN
        parameters = pika.URLParameters(self.broker_dsn)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def publish(self, message, queue_name, routing_key):
        # Declare the queue if it doesn't exist
        self.channel.queue_declare(queue=queue_name)

        # Publish the message to the queue with the specified routing key
        self.channel.basic_publish(
            exchange="topic_blockchain",
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            ),  # Make messages persistent
        )

        print(f"Message published: {json.dumps(message)}")

    def notify_add_record(self, record: Record):
        self.publish(record.to_json(), "my_queue", "blockchain.command.mine")

    def notify_show_chain(self):
        self.publish(None, "my_queue", "blockchain.command.show_chain")

    def notify_block_mined(self, block: Block):
        self.publish(block.to_json(), "my_queue", "blockchain.event.block_mined")

    def disconnect(self):
        # Close the connection to the broker
        self.connection.close()
        print("Disconnected from the broker.")


# Example usage:
if __name__ == "__main__":
    producer = Publisher()
    producer.connect()

    queue_name = "my_queue"
    routing_key = "blockchain.command.mine"
    record = Record(index=1, timestamp=int(time.time()), content="A new transaction")

    # producer.publish(message, queue_name, routing_key)
    producer.notify_add_record(record=record)
    producer.notify_show_chain()

    producer.disconnect()
