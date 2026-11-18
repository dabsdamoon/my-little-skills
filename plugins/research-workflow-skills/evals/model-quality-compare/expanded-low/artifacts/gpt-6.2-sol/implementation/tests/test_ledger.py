import unittest

from ledger import Ledger


def event(tenant, event_id, seq, amount):
    return dict(tenant=tenant, event_id=event_id, seq=seq, amount=amount)


class LedgerBehavior(unittest.TestCase):
    def test_interleaved_events_and_historical_replay(self):
        ledger = Ledger()
        original = event('a', 'first', 1, '9007199254740993.01')
        result = ledger.apply_batch(iter([
            original,
            event('b', 'first', 1, '2'),
            event('a', 'second', 2, '-0.02'),
            event('a', 'first', 1, '+09007199254740993.01'),
            event('a', 'third', 3, '0.01'),
        ]))
        self.assertEqual(result, [
            dict(tenant='a', event_id='first', applied=True, balance='9007199254740993.01'),
            dict(tenant='b', event_id='first', applied=True, balance='2.00'),
            dict(tenant='a', event_id='second', applied=True, balance='9007199254740992.99'),
            dict(tenant='a', event_id='first', applied=False, balance='9007199254740993.01'),
            dict(tenant='a', event_id='third', applied=True, balance='9007199254740993.00'),
        ])
        self.assertEqual(original, event('a', 'first', 1, '9007199254740993.01'))
        self.assertEqual(ledger.balance('a'), '9007199254740993.00')
        self.assertEqual(ledger.balance('b'), '2.00')

    def test_batch_rolls_back_across_tenants(self):
        ledger = Ledger()
        ledger.apply_batch([event('a', 'initial', 1, '3')])
        with self.assertRaises(ValueError):
            ledger.apply_batch([
                event('a', 'pending', 2, '-3'),
                event('b', 'pending', 1, '4'),
                event('a', 'overdraft', 3, '-0.01'),
            ])
        self.assertEqual(ledger.balance('a'), '3.00')
        self.assertEqual(ledger.balance('b'), '0.00')
        result = ledger.apply_batch([
            event('a', 'pending', 2, '1'),
            event('b', 'pending', 1, '2'),
        ])
        self.assertEqual([(r['applied'], r['balance']) for r in result],
                         [(True, '4.00'), (True, '2.00')])

    def test_iterator_exception_propagates_without_committing(self):
        ledger = Ledger()
        failure = RuntimeError('input failed')

        def broken():
            yield event('a', 'first', 1, '1')
            raise failure

        with self.assertRaises(RuntimeError) as caught:
            ledger.apply_batch(broken())
        self.assertIs(caught.exception, failure)
        self.assertEqual(ledger.balance('a'), '0.00')
        self.assertTrue(ledger.apply_batch([event('a', 'first', 1, '2')])[0]['applied'])

    def test_invalid_fields_and_sequence_gap(self):
        ledger = Ledger()
        valid = event('a', 'first', 1, '1')
        for update in (
            {'tenant': '  '}, {'event_id': ''}, {'seq': True}, {'seq': 0},
            {'seq': 2}, {'amount': 1.0}, {'amount': '1e0'}, {'amount': 'NaN'},
            {'amount': 'Infinity'}, {'amount': '1.001'}, {'amount': ' 1'},
        ):
            with self.subTest(update=update), self.assertRaises(ValueError):
                ledger.apply_batch([dict(valid, **update)])
        self.assertEqual(ledger.balance('a'), '0.00')
        self.assertEqual(ledger.apply_batch(iter(())), [])

    def test_replay_conflicts_leave_original_record_intact(self):
        ledger = Ledger()
        original = event('a', 'first', 1, '1')
        ledger.apply_batch([original])
        for conflict in (dict(original, amount='2'), dict(original, seq=2)):
            with self.subTest(conflict=conflict), self.assertRaises(ValueError):
                ledger.apply_batch([conflict])
        self.assertEqual(ledger.apply_batch([original]), [
            dict(tenant='a', event_id='first', applied=False, balance='1.00'),
        ])
