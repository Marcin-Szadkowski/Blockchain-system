import time
from unittest.mock import patch

import pytest

from blockchain_system.blockchain import PendingBlock, Record
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.services import mine_block


@pytest.fixture
def blockchain_repository():
    repo = BlockchainRepository()
    yield repo
    repo.chain = repo.chain[1:]


@pytest.fixture(scope="session")
def publisher_mock():
    with patch("blockchain_system.services.Publisher") as mck:
        yield mck


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
    publisher_mock,
):
    assert (
        mine_block(
            pending_blocks_repository=pending_blocks_repository,
            blockchain_repository=blockchain_repository,
        )
        == 1
    )
    assert pending_blocks_repository.pending_blocks_count() == 1

    assert (
        mine_block(
            pending_blocks_repository=pending_blocks_repository,
            blockchain_repository=blockchain_repository,
        )
        == 2
    )
    assert pending_blocks_repository.pending_blocks_count() == 0
    publisher_mock.return_value.notify_block_mined.assert_called()
