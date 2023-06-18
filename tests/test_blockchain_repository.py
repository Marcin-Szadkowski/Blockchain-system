import threading
import time

import pytest

from blockchain_system.blockchain import Block, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    StakeRegister,
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
        block = Block(0, "", [], 1234, [], "3434", 0)
        thread = threading.Thread(
            target=blockchain_repository.add_or_replace, args=(block,)
        )

        with locked_chain(blockchain_repository) as blockchain:
            thread.start()
            time.sleep(2)
            assert blockchain.length == 1

        thread.join()
        blockchain = blockchain_repository.get_chain()
        assert blockchain.length == 2


class TestStakeRegister:
    def test_initial_stake(self):
        register = StakeRegister()
        assert register.stake_map == {}

    def test_updated_stake_existing_address(self):
        register = StakeRegister({"addr1": 100, "addr2": 200})
        register.update_stake("addr1", 50)
        assert register.stake_map == {"addr1": 150, "addr2": 200}

    def test_updated_stake_new_address(self):
        register = StakeRegister({"addr1": 100})
        register.update_stake("addr2", 150)
        assert register.stake_map == {"addr1": 100, "addr2": 150}

    def test_get_highest_stake_addresses(self):
        register = StakeRegister(
            {"addr1": 300, "addr2": 200, "addr3": 400, "addr4": 100}
        )
        highest_stakes = register.get_highest_stake_addresses()
        assert highest_stakes == ["addr3", "addr1", "addr2", "addr4"]

    def test_get_highest_stake_addresses_empty(self):
        register = StakeRegister()
        highest_stakes = register.get_highest_stake_addresses()
        assert highest_stakes == []

    def test_get_highest_stake_addresses_single_address(self):
        register = StakeRegister({"addr1": 100})
        highest_stakes = register.get_highest_stake_addresses()
        assert highest_stakes == ["addr1"]
