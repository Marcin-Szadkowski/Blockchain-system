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
    content: typing.Any


@dataclass
class Block(JSONWizard):
    index: int
    previous_hash: str  # to be deleted
    timestamp: int  # UTC timestamp
    records: list[Record]  # or transactions
    hash: str | None = None

    def compute_hash(self):
        """
        Returns the hash of the block instance by first converting it
        into JSON string.
        """
        block_string = self.to_json()
        return hashlib.sha256(block_string.encode()).hexdigest()
