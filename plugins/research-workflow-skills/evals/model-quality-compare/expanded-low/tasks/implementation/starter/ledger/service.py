from .domain import amount
from .repository import MemoryState


class Ledger:
    def __init__(self):
        self.state = MemoryState()

    def balance(self, tenant):
        return f'{self.state.balances.get(tenant, 0):.2f}'

    def apply_batch(self, events):
        result = []
        for event in events:
            tenant = event['tenant']
            self.state.balances[tenant] = self.state.balances.get(tenant, 0) + amount(event['amount'])
            result.append({'tenant': tenant, 'event_id': event['event_id'],
                           'applied': True, 'balance': self.balance(tenant)})
        return result
