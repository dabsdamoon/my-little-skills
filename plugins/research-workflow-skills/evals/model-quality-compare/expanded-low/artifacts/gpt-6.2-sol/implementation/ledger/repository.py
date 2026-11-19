"""In-memory ledger state and its transaction-local updates."""

from typing import NamedTuple


class EventRecord(NamedTuple):
    seq: int
    cents: int
    balance: int


class MemoryState:
    def __init__(self):
        self._accounts = {}
        self._events = {}

    def copy(self):
        staged = MemoryState()
        staged._accounts = self._accounts.copy()
        staged._events = self._events.copy()
        return staged

    def balance(self, tenant):
        return self._accounts.get(tenant, (0, 0))[1]

    def apply(self, tenant, event_id, seq, cents):
        key = tenant, event_id
        record = self._events.get(key)
        if record is not None:
            if (seq, cents) != (record.seq, record.cents):
                raise ValueError('event ID was already used with a different sequence or amount')
            return False, record.balance

        last_seq, balance = self._accounts.get(tenant, (0, 0))
        if seq != last_seq + 1:
            raise ValueError('new events must have consecutive sequence numbers')
        balance += cents
        if balance < 0:
            raise ValueError('insufficient funds')

        self._accounts[tenant] = (seq, balance)
        self._events[key] = EventRecord(seq, cents, balance)
        return True, balance
