import logging

from blockchain_system.blockchain import Block, Blockchain, PendingBlock, Record
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.publisher import Publisher
from blockchain_system.services import (
    add_block,
    add_pending_block,
    set_chain,
    show_chain,
)

logger = logging.getLogger(__name__)


def handle_mine_block(payload):
    record = Record.from_json(payload)
    pending_block = PendingBlock(index=1, records=[record])
    add_pending_block(
        pending_blocks_repository=PendingBlocksRepository(),
        blockchain_repository=BlockchainRepository(),
        pending_block=pending_block,
    )


def handle_show_chain(payload):
    blockchain = show_chain(blockchain_repository=BlockchainRepository())
    publisher = Publisher()
    publisher.notify_event_show_chain(blockchain)


def handle_block_mined(payload):
    block = Block.from_json(payload)

    add_block(
        blockchain_repository=BlockchainRepository(), block=block, proof=block.hash
    )


def handle_new_node(payload):
    blockchain = show_chain(blockchain_repository=BlockchainRepository())
    publisher = Publisher()
    publisher.notify_event_show_chain(blockchain)


def handle_set_chain(payload):
    blockchain = Blockchain.from_json(payload)
    my_blockchain_copy = show_chain(blockchain_repository=BlockchainRepository())

    if blockchain.length <= my_blockchain_copy.length:
        return

    set_chain(blockchain=blockchain, blockchain_repository=BlockchainRepository())
