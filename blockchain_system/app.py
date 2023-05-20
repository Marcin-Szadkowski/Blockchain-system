import logging

from blockchain_system.publisher import Publisher
from blockchain_system.subscriber import Subscriber

logger = logging.getLogger(__name__)


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    )


def start_app():
    app = App(subscriber=Subscriber(), publisher=Publisher())
    app.start()


class App:
    def __init__(self, subscriber, publisher):
        self.subscriber = subscriber
        self.publisher = publisher

    def start(self):
        # TODO start mining thread
        logger.info("Starting app..")
        self.subscriber.start_consuming()


if __name__ == "__main__":
    setup_logger()
    start_app()
