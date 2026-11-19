"""Orchestration: validate, stage, commit atomically."""
from .domain import parse_event, format_cents
from .repository import MemoryState


class Ledger:
    def __init__(self):
        self.state = MemoryState()

    def balance(self, tenant):
        return format_cents(self.state.balances.get(tenant, 0))

    def apply_batch(self, events):
        tx = self.state.begin()
        result = []
        for event in events:  # iterator errors propagate before any commit
            tenant, event_id, seq, amt = parse_event(event)
            rec = tx.record((tenant, event_id))
            if rec is not None:
                if rec[:2] != (seq, amt):
                    raise ValueError('event key reused with different data')
                applied, bal = False, rec[2]
            else:
                if seq != tx.last_seq(tenant) + 1:
                    raise ValueError('non-consecutive seq')
                bal = tx.balance(tenant) + amt
                if bal < 0:
                    raise ValueError('insufficient funds')
                tx.put(tenant, event_id, seq, amt, bal)
                applied = True
            result.append({'tenant': tenant, 'event_id': event_id,
                           'applied': applied, 'balance': format_cents(bal)})
        tx.commit()
        return result
