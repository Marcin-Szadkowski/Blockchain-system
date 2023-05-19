import pika

from logging import getLogger

BROKER_DSN = "amqp://user:password@172.17.0.2:5672/"

logger = getLogger(__name__)
logger.setLevel("INFO")


# Create a connection to the RabbitMQ broker using the DSN
parameters = pika.URLParameters(BROKER_DSN)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare the direct exchange
channel.exchange_declare(exchange="topic_blockchain", exchange_type="topic")

# Declare a queue and bind it to the exchange with a routing key
queue_name = ""
routing_key = "blockchain.#"
channel.queue_declare(queue=queue_name)
channel.queue_bind(
    exchange="topic_blockchain", queue=queue_name, routing_key=routing_key
)


# Define the callback function to handle incoming messages
def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}. Routing key: {method.routing_key}")


# Set up the consumer to use the callback function
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# Start consuming messages
print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()
