import time
import pytest
from logging import getLogger
from blockchain_system.blockchain import Block, PendingBlock, Record
from blockchain_system.blockchain_repository import (
    BlockchainRepository,
    PendingBlocksRepository,
    StakeRegister,
)
from blockchain_system.signing_authority import generate_ecdsa_keys
from blockchain_system.services import (
    add_block_v2,
    add_pending_block,
    mint_block,
    show_chain,
    update_stake_register,
    vote_for_validators,
)

logger = getLogger(__name__)


class SimulatedNode:
    def __init__(
        self, private_key: str, address: str, balance: float | None = None
    ) -> None:
        self.private_key = private_key
        self.address = address
        self.balance = balance
        self.blockchain_repository = BlockchainRepository()
        self.pending_blocks_repository = PendingBlocksRepository()
        self.stake_register = StakeRegister()

    def set_initial_stake(self, stake_map: dict):
        for address, balance in stake_map.items():
            update_stake_register(address, balance, self.stake_register)

    def update_stake_register(self, address, delta):
        update_stake_register(address, delta, self.stake_register)

    def choose_validators(self) -> list[str]:
        return vote_for_validators(self.stake_register)

    def handle_vote_results(results) -> Block | None:
        # TODO validator validates transactions and adds the block
        pass

    def mint_block(self) -> Block | None:
        return mint_block(self.pending_blocks_repository, self.blockchain_repository)

    def register_new_pending_transaction(self, transaction):
        return add_pending_block(
            self.pending_blocks_repository,
            self.blockchain_repository,
            PendingBlock(0, records=transaction),
        )

    def add_or_reject_block(self, block, forger_address):
        return add_block_v2(self.blockchain_repository, block, forger_address)

    def show_chain(self):
        return show_chain(self.blockchain_repository)


@pytest.fixture
def transactions():
    return [Record(0, int(time.time() + i), f"Transaction {i}") for i in range(5)]


@pytest.fixture
def honest_nodes() -> list[SimulatedNode]:
    nodes = []

    for i in range(5):
        private_key, public_key = generate_ecdsa_keys()
        node = SimulatedNode(private_key, public_key, balance=i * 100)
        nodes.append(node)

    stake_map = map_stake(nodes)
    for node in nodes:
        node.set_initial_stake(stake_map)

    return nodes


def votes_to_validators(votes: list[list[str]], nodes) -> list[SimulatedNode]:
    validators_count = len(votes[0])

    count_votes = lambda votes: dict(
        (candidate, sum(1 for vote in votes if candidate in vote))
        for candidate in set(candidate for vote in votes for candidate in vote)
    )
    vote_counts = count_votes(votes)

    sorted_votes = dict(
        sorted(vote_counts.items(), key=lambda item: item[1], reverse=True)
    )
    top_x_keys = list(sorted_votes.keys())[:validators_count]

    return [validator for validator in nodes if validator.address in top_x_keys]


def map_stake(nodes: SimulatedNode) -> dict[str, float]:
    stake = {}
    for node in nodes:
        stake[node.address] = node.balance

    return stake


def test_proof_of_stake(transactions, honest_nodes: list[SimulatedNode]):
    for transaction in transactions:
        invalid_transaction = False
        transaction_accepted = False

        # for node in honest_nodes:
        #     node.register_new_pending_transaction(transaction)

        while not transaction_accepted:
            votes = []
            for node in honest_nodes:
                vote = node.choose_validators()
                votes.append(vote)

            # TODO we can balance votes based on stake
            validators = votes_to_validators(votes, honest_nodes)

            # choose firt valdiator to mint block
            validators[0].register_new_pending_transaction(transaction)
            maybe_block = validators[0].mint_block()
            if not maybe_block:
                continue
            accept_or_reject = []
            # TODO then some validators should check if block was valid
            for node in validators:
                maybe_accept = node.add_or_reject_block(
                    maybe_block, validators[0].address
                )
                accept_or_reject.append(maybe_accept)

            accepted = sum(accept_or_reject) > len(honest_nodes) / 2

            if not accepted:
                # TODO penalty for malicious node
                continue

            for node in honest_nodes:
                node.add_or_reject_block(maybe_block, validators[0].address)
            transaction_accepted = True

    logger.warning(honest_nodes[0].show_chain())
    assert len(honest_nodes[0].show_chain().chain) == len(transactions) + 1


def test_votes_to_validators():
    nodes = [
        SimulatedNode("", "addr1"),
        SimulatedNode("", "addr2"),
        SimulatedNode("", "addr3"),
    ]
    votes = [["addr1"], ["addr2"], ["addr3"], ["addr3"]]

    validators = votes_to_validators(votes, nodes)
    assert len(validators) == 1
    assert validators[0].address == "addr3"
