"""State ownership: committed state plus a staged transaction overlay."""


class MemoryState:
    def __init__(self):
        self.balances = {}   # tenant -> cents
        self.last_seq = {}   # tenant -> last applied seq
        self.applied = {}    # (tenant, event_id) -> (seq, cents, balance_after)

    def begin(self):
        return Transaction(self)


class Transaction:
    """Writes go to an overlay; nothing reaches MemoryState until commit()."""

    def __init__(self, state):
        self._s = state
        self._bal, self._seq, self._app = {}, {}, {}

    def balance(self, tenant):
        return self._bal.get(tenant, self._s.balances.get(tenant, 0))

    def last_seq(self, tenant):
        return self._seq.get(tenant, self._s.last_seq.get(tenant, 0))

    def record(self, key):
        return self._app.get(key) or self._s.applied.get(key)

    def put(self, tenant, event_id, seq, amount_cents, new_balance):
        self._bal[tenant] = new_balance
        self._seq[tenant] = seq
        self._app[(tenant, event_id)] = (seq, amount_cents, new_balance)

    def commit(self):
        self._s.balances.update(self._bal)
        self._s.last_seq.update(self._seq)
        self._s.applied.update(self._app)
