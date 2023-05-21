import threading
import time

import pytest

from blockchain_system.blockchain import Block, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    locked_chain,
)


@pytest.fixture
def pending_blocks_repository():
    repo = PendingBlocksRepository()
    yield repo
    repo.pending_blocks = []


@pytest.fixture
def blockchain_repository():
    repo = BlockchainRepository()
    yield repo
    repo.chain = repo.chain[1:]


class TestPendingBlockchainRepository:
    def test_add(self, pending_blocks_repository: PendingBlocksRepository):
        block = PendingBlock(index=0, records=[])
        pending_blocks_repository.add(block)
        assert pending_blocks_repository.pending_blocks_count() == 1

    def test_pop(self, pending_blocks_repository: PendingBlocksRepository):
        block1 = PendingBlock(index=0, records=[])
        block2 = PendingBlock(index=1, records=[])
        pending_blocks_repository.add(block1)
        pending_blocks_repository.add(block2)

        assert pending_blocks_repository.pending_blocks_count() == 2

        assert pending_blocks_repository.pop().index == 0
        assert pending_blocks_repository.pop().index == 1

    def test_locking(self, pending_blocks_repository: PendingBlocksRepository):
        block1 = PendingBlock(index=0, records=[])
        block2 = PendingBlock(index=1, records=[])

        thread = threading.Thread(target=pending_blocks_repository.add, args=(block1,))
        thread.start()

        pending_blocks_repository.add(block2)
        thread.join()

        assert pending_blocks_repository.pop().index == 0
        assert pending_blocks_repository.pop().index == 1


class TestBlockchainRepository:
    def test_get_chain(self, blockchain_repository: BlockchainRepository):
        block = Block(0, "0", 1234, [], "3434", 0)
        thread = threading.Thread(target=blockchain_repository.add, args=(block,))

        with locked_chain(blockchain_repository) as chain:
            thread.start()
            time.sleep(2)
            assert len(chain) == 1

        thread.join()
        chain = blockchain_repository.get_chain()
        assert len(chain) == 2
