import logging
import threading
import time
import uuid

from blockchain_system import settings
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.publisher import Publisher
from blockchain_system.services import mine_block
from blockchain_system.subscriber import Subscriber

logger = logging.getLogger(__name__)


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    )


def notify_new_node(publisher):
    time.sleep(5)
    publisher.notify_new_node()


def miner():
    blockchain_repository = BlockchainRepository()
    pending_blocks_repository = PendingBlocksRepository()

    while True:
        mined_block = mine_block(
            pending_blocks_repository=pending_blocks_repository,
            blockchain_repository=blockchain_repository,
        )
        if mined_block is None:
            logger.info("Nothing to mine. Waiting for transactions..")
            time.sleep(5)


def start_app():
    app = App(subscriber=Subscriber(), publisher=Publisher())
    app.start()


class App:
    def __init__(self, subscriber: Subscriber, publisher: Publisher):
        self.subscriber = subscriber
        self.publisher = publisher

    def start(self):
        my_uuid = uuid.uuid4().hex
        # # Settings
        settings.IS_TRUSTED_NODE.set(True)
        settings.MY_UUID.set(my_uuid)

        # # Start threads
        miner_thread = threading.Thread(target=miner, args=())
        notify_new_node_thread = threading.Thread(
            target=notify_new_node, args=(self.publisher,)
        )
        logger.info("Starting app..")
        miner_thread.start()
        notify_new_node_thread.start()
        self.subscriber.start_consuming()


if __name__ == "__main__":
    setup_logger()
    start_app()
