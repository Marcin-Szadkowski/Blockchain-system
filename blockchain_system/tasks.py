import logging

from blockchain_system.blockchain import PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.services import add_pending_block

logger = logging.getLogger(__name__)


def handle_mine_block(payload: dict):
    pending_block = PendingBlock.from_dict(payload)
    add_pending_block(
        pending_blocks_repository=PendingBlocksRepository(), pending_block=pending_block
    )


def handle_show_chain(payload):
    repository = BlockchainRepository()
    logger.info("Showing chain", current_chain=repository.get_chain())


def handle_block_mined(payload):
    print("handle block mined")
