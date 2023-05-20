import time

import pytest

from blockchain_system.blockchain import Block, PendingBlock, Record
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.services import mine_block


@pytest.fixture
def blockchain_repository():
    repo = BlockchainRepository()
    yield repo
    repo.chain = []


@pytest.fixture
def pending_blocks_repository():
    block1 = PendingBlock(
        index=1,
        records=[
            Record(index=0, timestamp=int(time.time()), content="First transaction")
        ],
    )
    block2 = PendingBlock(
        index=2,
        records=[
            Record(index=0, timestamp=int(time.time()), content="Second transaction")
        ],
    )
    repo = PendingBlocksRepository()
    repo.add(block1)
    repo.add(block2)

    yield repo

    repo.pending_blocks = []


def test_mine_block(
    blockchain_repository: BlockchainRepository,
    pending_blocks_repository: PendingBlocksRepository,
):
    assert (
        mine_block(
            pending_blocks_repository=pending_blocks_repository,
            blockchain_repository=blockchain_repository,
        )
        == 1
    )
    last_block: Block = blockchain_repository.get_last_block()

    assert len(last_block.records) == 1
    assert last_block.records[0].content == "First transaction"
    assert pending_blocks_repository.pending_blocks_count() == 1

    assert (
        mine_block(
            pending_blocks_repository=pending_blocks_repository,
            blockchain_repository=blockchain_repository,
        )
        == 2
    )

    last_block: Block = blockchain_repository.get_last_block()
    assert len(last_block.records) == 1
    assert last_block.records[0].content == "Second transaction"
    assert pending_blocks_repository.pending_blocks_count() == 0
