import copy
import random
import time
from logging import getLogger

from blockchain_system.blockchain import Block, Blockchain, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    StakeRegister,
    locked_chain,
)
from blockchain_system.publisher import Publisher

logger = getLogger(__name__)

POW_DIFFICULTY = 16
VALIDATORS_COUNT = 4
N = 2


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


def _get_side_links(n: int, blockchain_repository: BlockchainRepository):
    blockchain = blockchain_repository.get_chain()
    chain = copy.deepcopy(blockchain.chain)
    if len(chain) >= 1:
        chain.pop()

    if len(chain) <= n:
        return [block.hash for block in chain]
    else:
        return random.sample(chain, n)


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

    block.hash = proof
    blockchain_repository.add_or_replace(block)
    logger.info("Block added to the chain")
    return True


def mine_block(
    pending_blocks_repository: PendingBlocksRepository,
    blockchain_repository: BlockchainRepository,
) -> int | None:
    global N

    pending_block = pending_blocks_repository.pop()
    if not pending_block:
        return

    logger.info("Mining block")
    last_block = blockchain_repository.get_last_block()

    new_block = Block(
        index=pending_block.index,
        side_links=_get_side_links(N, blockchain_repository),
        records=pending_block.records,
        timestamp=int(time.time()),
        previous_hash=last_block.hash,
    )

    proof = _proof_of_work(new_block)
    publisher = Publisher()
    new_block.hash = proof
    publisher.notify_block_mined(block=new_block)
    return new_block.index


def show_chain(blockchain_repository: BlockchainRepository) -> Blockchain:
    blockchain = blockchain_repository.get_chain()
    return blockchain


def add_pending_block(
    pending_blocks_repository: PendingBlocksRepository,
    blockchain_repository: BlockchainRepository,
    pending_block: PendingBlock,
) -> None:
    with locked_chain(blockchain_repository) as chain:
        last_block = blockchain_repository.get_last_block()
        # recount actual index
        pending_block.index = (
            last_block.index + pending_blocks_repository.pending_blocks_count() + 1
        )
        pending_blocks_repository.add(block=pending_block)
    logger.info("New pending block added")


def mint_block(
    pending_blocks_repository: PendingBlocksRepository,
    blockchain_repository: BlockchainRepository,
):
    logger.info("Minting block.")
    pending_block = pending_blocks_repository.pop()
    if not pending_block:
        return

    last_block = blockchain_repository.get_last_block()

    new_block = Block(
        index=pending_block.index,
        side_links=_get_side_links(N, blockchain_repository),
        records=pending_block.records,
        timestamp=int(time.time()),
        previous_hash=last_block.hash,
    )
    new_block.hash = new_block.compute_hash()
    return new_block


def add_block_v2(
    blockchain_repository: BlockchainRepository,
    block: Block,
    forger_address: str,
):
    blockchain_repository.add_or_replace(block)
    logger.info("Block added to the chain")
    return True


def update_stake_register(
    address: str,
    delta: float,
    stake_register: StakeRegister,
) -> None:
    logger.info(f"Registering stake difference")
    stake_register.update_stake(address=address, delta=delta)


def vote_for_validators(
    stake_register: StakeRegister,
) -> list[str]:
    """
    Return list of address of candidates.
    """
    highest_to_lowest_stake = stake_register.get_highest_stake_addresses()

    return highest_to_lowest_stake[:VALIDATORS_COUNT]


def vote_for_miner(*args, **kwargs):
    # pass publisher as dependency
    pass


def _calculate_stake(*args, **kwargs):
    pass


def _verify_signature(*args, **kwargs):
    pass
