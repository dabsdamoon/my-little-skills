import unittest
from ledger import Ledger


def ev(t, i, s, a):
    return {'tenant': t, 'event_id': i, 'seq': s, 'amount': a}


class Behavior(unittest.TestCase):
    def test_exact_big_money(self):
        l = Ledger()
        l.apply_batch([ev('a', 'x', 1, '9007199254740993.01')])
        self.assertEqual(l.balance('a'), '9007199254740993.01')

    def test_replay_returns_original_balance(self):
        l = Ledger()
        l.apply_batch([ev('a', 'x', 1, '5')])
        l.apply_batch([ev('a', 'y', 2, '5')])
        r = l.apply_batch([ev('a', 'x', 1, '5.00')])
        self.assertEqual(r[0]['applied'], False)
        self.assertEqual(r[0]['balance'], '5.00')
        self.assertEqual(l.balance('a'), '10.00')
        l.apply_batch([ev('a', 'z', 3, '1')])

    def test_reuse_conflict(self):
        l = Ledger()
        l.apply_batch([ev('a', 'x', 1, '5')])
        for e in (ev('a', 'x', 1, '6'), ev('a', 'x', 2, '5')):
            with self.assertRaises(ValueError):
                l.apply_batch([e])

    def test_atomic_and_interleaved(self):
        l = Ledger()
        with self.assertRaises(ValueError):
            l.apply_batch([ev('a', 'x', 1, '5'), ev('b', 'x', 1, '1'), ev('a', 'y', 2, '-9')])
        self.assertEqual(l.balance('a'), '0.00')
        r = l.apply_batch([ev('a', 'x', 1, '5'), ev('b', 'x', 1, '1'), ev('a', 'y', 2, '-5')])
        self.assertEqual([x['balance'] for x in r], ['5.00', '1.00', '0.00'])

    def test_iterator_error(self):
        l = Ledger()
        def gen():
            yield ev('a', 'x', 1, '5')
            raise RuntimeError('boom')
        with self.assertRaises(RuntimeError):
            l.apply_batch(gen())
        self.assertEqual(l.balance('a'), '0.00')
        self.assertEqual(l.apply_batch(iter([ev('a', 'x', 1, '5')]))[0]['applied'], True)

    def test_invalid(self):
        bad = [ev('a', 'x', 2, '1'), ev('a', 'x', 0, '1'), ev('a', 'x', True, '1'),
               ev('a', 'x', 1, '1e2'), ev('a', 'x', 1, '1.234'), ev('a', 'x', 1, 1.5),
               ev('a', 'x', 1, 'NaN'), ev(' ', 'x', 1, '1'), ev('a', '', 1, '1'),
               ev('a', 'x', 1, '-1')]
        for e in bad:
            with self.assertRaises(ValueError, msg=e):
                Ledger().apply_batch([e])

    def test_no_mutation_and_empty(self):
        e = ev('a', 'x', 1, '1')
        c = dict(e)
        l = Ledger()
        self.assertEqual(l.apply_batch([]), [])
        l.apply_batch([e])
        self.assertEqual(e, c)


if __name__ == '__main__':
    unittest.main()
