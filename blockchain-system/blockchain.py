# TODO:
#  A simple consensus algorithm could be to agree upon the longest valid chain when the chains of different participating nodes
#  in the network appear to diverge. The rationale behind this approach is that the longest chain is a good estimate of the most
#  amount of work done (remember proof of work is difficult to compute):

import datetime
import hashlib
import json
import typing
from dataclasses import dataclass

from dataclass_wizard import JSONWizard


@dataclass
class Block(JSONWizard):
    index: int
    main_hash: str
    extra_hashes: list[str]
    proof: str  # Proof of Work
    timestamp: int  # UTC timestamp
    records: list  # or transactions


class Record(JSONWizard):
    index: int
    timestamp: int
    content: typing.Any


class Blockchain:
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain: list[Block] = []
        self.create_block(proof=1, previous_hash="0")

    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.chain.append(block)
        return block

    # This function is created
    # to display the previous block
    def print_previous_block(self):
        return self.chain[-1]

    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:5] == "00000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()
            ).hexdigest()

            if hash_operation[:5] != "00000":
                return False
            previous_block = block
            block_index += 1

        return True
