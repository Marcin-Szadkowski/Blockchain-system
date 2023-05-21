import hashlib
import typing
from dataclasses import dataclass

from dataclass_wizard import JSONWizard


@dataclass
class PendingBlock(JSONWizard):
    index: int
    records: list


@dataclass
class Record(JSONWizard):
    index: int
    timestamp: int
    content: str


@dataclass
class Block(JSONWizard):
    index: int
    previous_hash: str  # to be deleted
    timestamp: int  # UTC timestamp
    records: list[Record]  # or transactions
    hash: str | None = None
    nonce: int = 0

    def compute_hash(self):
        """
        Returns the hash of the block instance by first converting it
        into JSON string.
        """
        block_string = str(self.to_dict(exclude=["hash"]))
        return hashlib.sha256(block_string.encode()).hexdigest()


@dataclass
class Blockchain(JSONWizard):
    chain: list[Block]

    @property
    def length(self):
        return len(self.chain)
