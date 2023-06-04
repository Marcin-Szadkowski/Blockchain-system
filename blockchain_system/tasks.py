import json
import logging

from blockchain_system.blockchain import Block, Blockchain, PendingBlock, Record, Vote
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
)
from blockchain_system.publisher import Publisher
from blockchain_system.services import (
    add_authority_node,
    add_block,
    add_pending_block,
    am_i_trusted_node,
    get_authority_proof,
    get_my_uuid,
    set_chain,
    show_chain,
    vote_for_miner,
)

logger = logging.getLogger(__name__)


def handle_mine_block(payload):
    record = Record.from_json(payload)
    # pending_block = PendingBlock(index=1, records=[record])
    # add_pending_block(
    #     pending_blocks_repository=PendingBlocksRepository(),
    #     blockchain_repository=BlockchainRepository(),
    #     pending_block=pending_block,
    # )
    if am_i_trusted_node():
        return

    publisher = Publisher()
    miner = vote_for_miner()
    my_vote = Vote(node_id=miner, records=[record])

    publisher.notify_node_voted(my_vote)


def handle_show_chain(payload):
    blockchain = show_chain(blockchain_repository=BlockchainRepository())
    publisher = Publisher()
    publisher.notify_event_show_chain(blockchain)


def handle_block_mined(payload):
    block = Block.from_json(payload)

    add_block(
        blockchain_repository=BlockchainRepository(), block=block, proof=block.hash
    )


def handle_new_node(payload):
    blockchain = show_chain(blockchain_repository=BlockchainRepository())
    publisher = Publisher()
    logger.info(f"Is authority node: {am_i_trusted_node()}")
    publisher.notify_set_chain(blockchain)

    if am_i_trusted_node():
        my_uuid = get_my_uuid()
        publisher.notify_authority_node_says_hello(
            my_uuid, get_authority_proof(my_uuid)
        )


def handle_set_chain(payload):
    blockchain = Blockchain.from_json(payload)
    my_blockchain_copy = show_chain(blockchain_repository=BlockchainRepository())

    if blockchain.length <= my_blockchain_copy.length:
        return

    set_chain(blockchain=blockchain, blockchain_repository=BlockchainRepository())


def handle_node_voted(payload):
    vote = Vote.from_json(payload)
    my_uuid = get_my_uuid()

    if my_uuid and my_uuid == vote.node_id:
        logger.info("Nodes voted for me. Adding pending block.")
        pending_block = PendingBlock(index=1, records=vote.records)
        add_pending_block(
            pending_blocks_repository=PendingBlocksRepository(),
            blockchain_repository=BlockchainRepository(),
            pending_block=pending_block,
        )


def handle_authority_node_says_hello(payload):
    node_id = payload["id"]
    proof = payload["proof"]

    logger.info(f"Discovered authority node: {node_id}")
    add_authority_node(node_id, proof)
