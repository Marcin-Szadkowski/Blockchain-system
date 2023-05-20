import time
from logging import getLogger

from blockchain_system.blockchain import Block, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    locked_chain,
)

logger = getLogger(__name__)

POW_DIFFICULTY = 0


class InvalidProofException(Exception):
    pass


def _proof_of_work(block: Block):
    block.nonce = 0

    computed_hash = block.compute_hash()
    while not computed_hash.startswith("0" * POW_DIFFICULTY):
        block.nonce += 1
        computed_hash = block.compute_hash()

    return computed_hash


def _is_valid_proof(block, block_hash):
    return (
        block_hash.startswith("0" * POW_DIFFICULTY)
        and block_hash == block.compute_hash()
    )


def add_block(blockchain_repository: BlockchainRepository, block: Block, proof: str):
    if not _is_valid_proof(block, proof):
        raise InvalidProofException()

    block.hash = proof
    blockchain_repository.add(block)
    logger.info("Block added to the chain", index=block.index)
    return True


def mine_block(
    pending_blocks_repository: PendingBlocksRepository,
    blockchain_repository: BlockchainRepository,
):
    pending_block = pending_blocks_repository.pop()
    if not pending_block:
        return

    logger.info("Mining block", records=pending_block.records)
    last_block = blockchain_repository.get_last_block()

    new_block = Block(
        index=last_block.index + 1,
        records=pending_block.records,
        timestamp=int(time.time()),
        previous_hash=last_block.hash,
    )

    proof = _proof_of_work(new_block)
    add_block(
        blockchain_repository=blockchain_repository,
        block=new_block,
        proof=proof,
    )
    # TODO notify block mined
    return new_block.index


def show_chain(blockchain_repository: BlockchainRepository):
    chain = blockchain_repository.get_chain()
    logger.info(f"Showing chain:{chain}")


def add_pending_block(
    pending_blocks_repository: PendingBlocksRepository, pending_block: PendingBlock
):
    pending_blocks_repository.add(block=pending_block)
    logger.info("New pending block added", index=pending_block.index)
