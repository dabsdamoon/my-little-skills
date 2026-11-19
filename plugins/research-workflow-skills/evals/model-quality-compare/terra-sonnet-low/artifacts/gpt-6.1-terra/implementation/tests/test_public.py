import unittest
from ledger import Ledger


class PublicBehavior(unittest.TestCase):
    def test_deposit(self):
        ledger = Ledger()
        result = ledger.apply_batch([{'tenant':'a','event_id':'one','seq':1,'amount':'10.00'}])
        self.assertEqual(result, [{'tenant':'a','event_id':'one','applied':True,'balance':'10.00'}])

    def test_independent_balance(self):
        ledger = Ledger()
        ledger.apply_batch([{'tenant':'a','event_id':'one','seq':1,'amount':'10.00'}])
        self.assertEqual(ledger.balance('b'),'0.00')


if __name__ == '__main__': unittest.main()
