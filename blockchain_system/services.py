import abc
import copy
import random
import time
from logging import getLogger

from blockchain_system import settings
from blockchain_system.blockchain import Block, Blockchain, PendingBlock
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    locked_chain,
)
from blockchain_system.publisher import Publisher

logger = getLogger(__name__)

POW_DIFFICULTY = 16
N = 2


class InvalidProofException(Exception):
    pass


class InvalidBlockchainException(Exception):
    pass


class ISystemAuthority(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_authority_proof(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def verify_authority_proof(self, *args, **kwargs) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def am_i_trusted_node(self, *args, **kwargs) -> bool:
        raise NotImplementedError()


class DummySystemAuthority(ISystemAuthority):
    def get_authority_proof(self, node_id: str) -> str:
        return node_id

    def verify_authority_proof(self, proof: str):
        return True

    def am_i_trusted_node(self, *args, **kwargs) -> bool:
        return settings.IS_TRUSTED_NODE.get()


def am_i_trusted_node() -> bool:
    system_authority = DummySystemAuthority()
    return system_authority.am_i_trusted_node()


def get_my_uuid() -> str | None:
    return settings.MY_UUID.get()


def _proof_of_work(block: Block):
    block.nonce = 0

    computed_hash = block.compute_hash()
    hash_bin = format(int(computed_hash, 16), "0>256b")

    while not hash_bin.startswith("0" * POW_DIFFICULTY):
        block.nonce += 1
        computed_hash = block.compute_hash()
        hash_bin = format(int(computed_hash, 16), "0>256b")

    return computed_hash


def _is_valid_proof(block: Block, block_hash) -> bool:
    hash_bin = format(int(block_hash, 16), "0>256b")
    return (
        hash_bin.startswith("0" * POW_DIFFICULTY) and block_hash == block.compute_hash()
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


def vote_for_miner() -> str:
    """
    Returns uuid of miner. Assume that there is at least one authority node in system.
    """
    known_miners = settings.KNOWN_MINERS_LIST.get()
    if known_miners is None:
        logger.error("Cannot vote for miner. Cannot find any.")
        return

    return random.sample(known_miners, 1)[0]


def add_authority_node(node_id: str, authority_proof: str) -> None:
    known_miners_list = settings.KNOWN_MINERS_LIST.get()

    if not node_id in known_miners_list and verify_authority_proof(authority_proof):
        logger.info("Updated known miners list.")
        known_miners_list.append(node_id)
        settings.KNOWN_MINERS_LIST.set(known_miners_list)


def get_authority_proof(node_id: str) -> str:
    system_authority = DummySystemAuthority()
    return system_authority.get_authority_proof(node_id=node_id)


def verify_authority_proof(authority_proof: str) -> bool:
    system_authority = DummySystemAuthority()
    return system_authority.verify_authority_proof(authority_proof)
