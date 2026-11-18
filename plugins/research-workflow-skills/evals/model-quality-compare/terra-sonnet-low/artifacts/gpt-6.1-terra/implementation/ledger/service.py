from .domain import format_amount, validate_event
from .repository import MemoryState


class Ledger:
    def __init__(self):
        self.state = MemoryState()

    def balance(self, tenant):
        return format_amount(self.state.balances.get(tenant, 0))

    def apply_batch(self, events):
        # Work solely on a snapshot until the iterable has been exhausted.
        state = self.state.copy()
        result = []
        for event in events:
            tenant, event_id, seq, cents = validate_event(event)
            key = (tenant, event_id)
            if key in state.events:
                original_seq, original_cents, original_balance = state.events[key]
                if (seq, cents) != (original_seq, original_cents):
                    raise ValueError('event id reused with different contents')
                applied = False
                balance = original_balance
            else:
                if seq != state.sequences.get(tenant, 0) + 1:
                    raise ValueError('events must have consecutive sequence numbers')
                balance = state.balances.get(tenant, 0) + cents
                if balance < 0:
                    raise ValueError('insufficient funds')
                state.balances[tenant] = balance
                state.sequences[tenant] = seq
                state.events[key] = (seq, cents, balance)
                applied = True
            result.append({'tenant': tenant, 'event_id': event_id,
                           'applied': applied, 'balance': format_amount(balance)})
        self.state = state
        return result
