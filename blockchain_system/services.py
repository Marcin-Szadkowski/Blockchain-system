import time
from logging import getLogger

from blockchain_system.blockchain import Block, Blockchain, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    locked_chain,
)
from blockchain_system.publisher import Publisher

logger = getLogger(__name__)

POW_DIFFICULTY = 1


class InvalidProofException(Exception):
    pass


class InvalidBlockchainException(Exception):
    pass


def _proof_of_work(block: Block):
    block.nonce = 0

    computed_hash = block.compute_hash()
    while not computed_hash.startswith("0" * POW_DIFFICULTY):
        block.nonce += 1
        computed_hash = block.compute_hash()

    return computed_hash


def _is_valid_proof(block: Block, block_hash) -> bool:
    return (
        block_hash.startswith("0" * POW_DIFFICULTY)
        and block_hash == block.compute_hash()
    )


def check_chain_validity(blockchain: Blockchain):
    previous_hash = "0"

    for block in blockchain.chain:
        if (
            not _is_valid_proof(block, block.hash)
            or previous_hash != block.previous_hash
        ):
            return False
        previous_hash = block.hash

    return True


def set_chain(
    blockchain: Blockchain, blockchain_repository: BlockchainRepository
) -> None:
    if not check_chain_validity(blockchain):
        raise InvalidBlockchainException()

    blockchain_repository.set_chain(blockchain)
    logger.info("Chain updated")


def add_block(
    blockchain_repository: BlockchainRepository, block: Block, proof: str
) -> bool:
    if not _is_valid_proof(block, proof):
        raise InvalidProofException()

    # TODO check timestamp
    block.hash = proof
    blockchain_repository.add(block)
    logger.info("Block added to the chain")
    return True


def mine_block(
    pending_blocks_repository: PendingBlocksRepository,
    blockchain_repository: BlockchainRepository,
) -> int | None:
    pending_block = pending_blocks_repository.pop()
    if not pending_block:
        return

    logger.info("Mining block")
    last_block = blockchain_repository.get_last_block()

    new_block = Block(
        index=last_block.index + 1,
        records=pending_block.records,
        timestamp=int(time.time()),
        previous_hash=last_block.hash,
    )

    proof = _proof_of_work(new_block)
    # add_block(
    #     blockchain_repository=blockchain_repository,
    #     block=new_block,
    #     proof=proof,
    # )
    # TODO notify block mined
    publisher = Publisher()
    new_block.hash = proof
    publisher.notify_block_mined(block=new_block)
    return new_block.index


def show_chain(blockchain_repository: BlockchainRepository) -> Blockchain:
    chain = blockchain_repository.get_chain()
    return Blockchain(chain=chain)


def add_pending_block(
    pending_blocks_repository: PendingBlocksRepository, pending_block: PendingBlock
) -> None:
    pending_blocks_repository.add(block=pending_block)
    logger.info("New pending block added")
