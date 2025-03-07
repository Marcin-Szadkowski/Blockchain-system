import threading
import time
from contextlib import contextmanager
from copy import deepcopy

from blockchain_system.blockchain import Block, Blockchain, PendingBlock


@contextmanager
def locked_chain(blockchain_repository: "BlockchainRepository"):
    blockchain_repository._lock.acquire()

    try:
        yield blockchain_repository.get_chain()
    finally:
        blockchain_repository._lock.release()


class PreviousHashMismatchException(Exception):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BlockchainRepository(metaclass=Singleton):
    def __init__(self):
        self.chain: list[Block] = []
        self._lock = threading.Lock()
        genesis_block = self.create_genesis_block()
        self.add_or_replace(genesis_block)

    def create_genesis_block(self) -> Block:
        genesis_block = Block(
            index=0,
            previous_hash="0",
            side_links=[],
            hash="",
            timestamp=int(time.time()),
            records=[],
        )
        genesis_block.main_hash = genesis_block.compute_hash()
        return genesis_block

    def add_or_replace(self, block: Block) -> None:
        with self._lock:
            last_block = self.get_last_block()
            if self._is_in_chain(block_to_add=block, last_block=last_block):
                # Replace
                self.chain[-1] = block
                return

            if last_block and last_block.hash != block.previous_hash:
                raise PreviousHashMismatchException()
            self.chain.append(block)

    def _is_in_chain(self, block_to_add: Block, last_block: Block) -> None:
        penultimate_block = self.chain[-2] if len(self.chain) >= 2 else None

        if not penultimate_block:
            return False

        if (
            block_to_add.index == last_block.index
            and penultimate_block.hash == block_to_add.previous_hash
            and block_to_add.timestamp < last_block.timestamp
        ):
            return True

        return False

    def get_chain(self) -> Blockchain:
        return Blockchain(chain=self.chain)

    def set_chain(self, blockchain: Blockchain) -> None:
        with self._lock:
            self.chain = blockchain.chain

    def get_last_block(self) -> Block:
        if not self.chain:
            return

        return self.chain[-1]


class PendingBlocksRepository(metaclass=Singleton):
    def __init__(self):
        self.pending_blocks = []
        self._lock = threading.Lock()

    def pending_blocks_count(self) -> int:
        return len(self.pending_blocks)

    def add(self, block: PendingBlock) -> None:
        with self._lock:
            self.pending_blocks.append(block)

    def pop(self) -> PendingBlock:
        """First in first out"""
        if not self.pending_blocks:
            return

        with self._lock:
            if len(self.pending_blocks) == 1:
                popped_block = self.pending_blocks[0]
                self.pending_blocks = []
                return popped_block

            temp = deepcopy(self.pending_blocks[1:])
            popped_block = self.pending_blocks[0]
            self.pending_blocks = temp

        return popped_block
