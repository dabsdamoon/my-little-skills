"""In-memory state and isolated batch snapshots."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Receipt:
    seq: int
    cents: int
    balance: int


class MemoryState:
    def __init__(self):
        self.balances = {}
        self.sequences = {}
        self.receipts = {}

    def snapshot(self):
        staged = MemoryState()
        staged.balances = self.balances.copy()
        staged.sequences = self.sequences.copy()
        staged.receipts = self.receipts.copy()
        return staged
