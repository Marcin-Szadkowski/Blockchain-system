import pika

BROKER_DSN = "amqp://user:password@172.17.0.2:5672/"


class Producer:
    def __init__(self, broker_dsn):
        self.connection = None
        self.channel = None
        self.broker_dsn = broker_dsn

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
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            ),  # Make messages persistent
        )

        print(f"Message published: {message}")

    def disconnect(self):
        # Close the connection to the broker
        self.connection.close()
        print("Disconnected from the broker.")


# Example usage:
if __name__ == "__main__":
    producer = Producer(BROKER_DSN)
    producer.connect()

    queue_name = "my_queue"
    routing_key = "blockchain.command.mine"
    message = "Hello, consumer!"

    producer.publish(message, queue_name, routing_key)

    producer.disconnect()
