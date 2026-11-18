import copy
import unittest

from ledger import Ledger


def event(tenant='a', event_id='one', seq=1, amount='10.00'):
    return dict(tenant=tenant, event_id=event_id, seq=seq, amount=amount)


class LedgerContract(unittest.TestCase):
    def test_exact_money_and_input_preservation(self):
        ledger = Ledger()
        events = [event(amount='9007199254740993.01'),
                  event(event_id='two', seq=2, amount='0.02')]
        original = copy.deepcopy(events)
        results = ledger.apply_batch(iter(events))
        self.assertEqual(events, original)
        self.assertEqual(results[-1], dict(tenant='a', event_id='two',
                                          applied=True, balance='9007199254740993.03'))
        self.assertEqual(ledger.balance('a'), '9007199254740993.03')

    def test_interleaving_and_historical_replays(self):
        ledger = Ledger()
        results = ledger.apply_batch([
            event(amount='10'), event(tenant='b', amount='2'),
            event(event_id='two', seq=2, amount='-3'),
            event(amount='+10.0'), event(event_id='three', seq=3, amount='-7')])
        self.assertEqual([r['applied'] for r in results], [True, True, True, False, True])
        self.assertEqual([r['balance'] for r in results], ['10.00', '2.00', '7.00', '10.00', '0.00'])
        self.assertEqual(ledger.apply_batch([event(amount='10.00')])[0]['balance'], '10.00')
        self.assertEqual(ledger.balance('a'), '0.00')
        self.assertEqual(ledger.balance('b'), '2.00')

    def test_invalid_events(self):
        bad = [None, [], {}, event(tenant=' '), event(event_id=''),
               event(seq=True), event(seq=0), event(seq=1.0), event(seq='1')]
        bad += [event(amount=x) for x in [1, 1.2, None, '', ' 1', '1 ', '1e2',
                                         'NaN', 'Infinity', '1.001', '--1', '1\n']]
        for invalid in bad:
            with self.subTest(invalid=invalid):
                ledger = Ledger()
                with self.assertRaises(ValueError):
                    ledger.apply_batch([event(tenant='b'), invalid])
                self.assertEqual(ledger.balance('b'), '0.00')
                self.assertTrue(ledger.apply_batch([event(tenant='b')])[0]['applied'])

    def test_conflicts_gaps_and_overdraft_roll_back_everything(self):
        for invalid in [event(amount='11'), event(seq=2),
                        event(event_id='gap', seq=3),
                        event(event_id='debit', seq=2, amount='-10.01')]:
            with self.subTest(invalid=invalid):
                ledger = Ledger()
                ledger.apply_batch([event()])
                with self.assertRaises(ValueError):
                    ledger.apply_batch([event(tenant='b'), invalid])
                self.assertEqual(ledger.balance('a'), '10.00')
                self.assertEqual(ledger.balance('b'), '0.00')
                self.assertTrue(ledger.apply_batch([event(tenant='b')])[0]['applied'])
                self.assertTrue(ledger.apply_batch([event(event_id='next', seq=2)])[0]['applied'])

    def test_iterator_exception_propagates_and_rolls_back(self):
        ledger = Ledger()
        failure = RuntimeError('input failed')

        def events():
            yield event()
            yield event(tenant='b')
            raise failure

        with self.assertRaises(RuntimeError) as caught:
            ledger.apply_batch(events())
        self.assertIs(caught.exception, failure)
        self.assertEqual(ledger.balance('a'), '0.00')
        self.assertEqual(ledger.balance('b'), '0.00')
        self.assertTrue(ledger.apply_batch([event()])[0]['applied'])

    def test_empty_and_zero_normalization(self):
        ledger = Ledger()
        self.assertEqual(ledger.apply_batch(iter([])), [])
        self.assertEqual(ledger.balance('missing'), '0.00')
        results = ledger.apply_batch([event(amount='-0.00'), event(amount='+0')])
        self.assertEqual(results, [dict(tenant='a', event_id='one', applied=True, balance='0.00'),
                                   dict(tenant='a', event_id='one', applied=False, balance='0.00')])


if __name__ == '__main__':
    unittest.main()
