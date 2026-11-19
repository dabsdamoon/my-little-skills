"""Batch orchestration and ledger transition rules."""
from .domain import Event, format_money
from .repository import MemoryState, Receipt


class Ledger:
    def __init__(self):
        self.state = MemoryState()

    def balance(self, tenant):
        return format_money(self.state.balances.get(tenant, 0))

    def apply_batch(self, events):
        staged = self.state.snapshot()
        result = []
        for raw in events:
            event = Event.parse(raw)
            key = (event.tenant, event.event_id)
            receipt = staged.receipts.get(key)
            applied = receipt is None
            if receipt is not None:
                if (receipt.seq, receipt.cents) != (event.seq, event.cents):
                    raise ValueError('idempotency key reused with different contents')
            else:
                if event.seq != staged.sequences.get(event.tenant, 0) + 1:
                    raise ValueError('new events must have consecutive sequence numbers')
                balance = staged.balances.get(event.tenant, 0) + event.cents
                if balance < 0:
                    raise ValueError('insufficient funds')
                receipt = Receipt(event.seq, event.cents, balance)
                staged.balances[event.tenant] = balance
                staged.sequences[event.tenant] = event.seq
                staged.receipts[key] = receipt
            result.append({'tenant': event.tenant, 'event_id': event.event_id,
                           'applied': applied, 'balance': format_money(receipt.balance)})
        # Commit only after successful exhaustion, including iterator finalization.
        self.state = staged
        return result
