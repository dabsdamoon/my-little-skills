"""In-memory ledger state and transaction snapshots."""


class MemoryState:
    def __init__(self):
        self.balances = {}
        self.sequences = {}
        self.events = {}

    def copy(self):
        snapshot = MemoryState()
        snapshot.balances = self.balances.copy()
        snapshot.sequences = self.sequences.copy()
        snapshot.events = self.events.copy()
        return snapshot
