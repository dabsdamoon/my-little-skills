import unittest

from ledger import Ledger


def event(tenant, event_id, seq, amount):
    return dict(tenant=tenant, event_id=event_id, seq=seq, amount=amount)


class LedgerBehavior(unittest.TestCase):
    def test_interleaved_replay_and_exact_money(self):
        ledger = Ledger()
        events = [event('a', 'x', 1, '9007199254740993.01'),
                  event('b', 'x', 1, '2'), event('a', 'y', 2, '-0.01'),
                  event('a', 'x', 1, '9007199254740993.010'[:-1])]
        self.assertEqual(ledger.apply_batch(iter(events)), [
            dict(tenant='a', event_id='x', applied=True, balance='9007199254740993.01'),
            dict(tenant='b', event_id='x', applied=True, balance='2.00'),
            dict(tenant='a', event_id='y', applied=True, balance='9007199254740993.00'),
            dict(tenant='a', event_id='x', applied=False, balance='9007199254740993.01')])
        self.assertEqual(ledger.balance('a'), '9007199254740993.00')
        self.assertEqual(ledger.apply_batch([event('b', 'x', 1, '2.00')])[0]['applied'], False)

    def test_atomic_failure_and_iterator_exception(self):
        ledger = Ledger()
        ledger.apply_batch([event('a', 'start', 1, '3')])
        def broken():
            yield event('a', 'next', 2, '1')
            yield event('b', 'first', 1, '5')
            raise RuntimeError('input failed')
        with self.assertRaisesRegex(RuntimeError, 'input failed'):
            ledger.apply_batch(broken())
        with self.assertRaises(ValueError):
            ledger.apply_batch([event('b', 'first', 1, '5'), event('a', 'next', 2, '-4')])
        self.assertEqual(ledger.balance('a'), '3.00')
        self.assertEqual(ledger.balance('b'), '0.00')
        self.assertTrue(ledger.apply_batch([event('a', 'next', 2, '1'), event('b', 'first', 1, '5')])[0]['applied'])

    def test_invalid_events_and_conflicts(self):
        ledger = Ledger()
        ledger.apply_batch([event('a', 'x', 1, '1')])
        bad = [event('a', 'x', 1, '2'), event('a', 'x', 2, '1'),
               event('a', 'y', 3, '1'), event(' ', 'y', 2, '1'),
               event('a', '', 2, '1'), event('a', 'y', True, '1'),
               event('a', 'y', 2, 1.0), event('a', 'y', 2, '1e2'),
               event('a', 'y', 2, 'NaN'), event('a', 'y', 2, '1.001'), {}]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(ValueError):
                ledger.apply_batch([item])
        self.assertEqual(ledger.balance('a'), '1.00')
        self.assertEqual(ledger.apply_batch([]), [])
        self.assertEqual(ledger.apply_batch([event('a', 'y', 2, '-1')])[0]['balance'], '0.00')

    def test_input_unchanged(self):
        ledger = Ledger()
        item = event('a', 'x', 1, '+01.0')
        original = item.copy()
        ledger.apply_batch([item])
        self.assertEqual(item, original)
        self.assertFalse(ledger.apply_batch([event('a', 'x', 1, '1.00')])[0]['applied'])
