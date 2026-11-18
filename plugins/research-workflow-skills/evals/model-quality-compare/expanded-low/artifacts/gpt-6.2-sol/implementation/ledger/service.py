from .domain import format_balance, validate_event
from .repository import MemoryState


class Ledger:
    def __init__(self):
        self._state = MemoryState()

    def balance(self, tenant):
        return format_balance(self._state.balance(tenant))

    def apply_batch(self, events):
        staged = self._state.copy()
        result = []
        for event in events:
            tenant, event_id, seq, cents = validate_event(event)
            applied, balance = staged.apply(tenant, event_id, seq, cents)
            result.append({'tenant': tenant, 'event_id': event_id,
                           'applied': applied, 'balance': format_balance(balance)})
        self._state = staged
        return result
