import copy
import io
import json
import sys
import unittest
sys.path.insert(0, '/workspace')
from ledger import Ledger


def event(id='one', seq=1, amount='10.00', tenant='a'):
    return dict(tenant=tenant,event_id=id,seq=seq,amount=amount)


class Acceptance(unittest.TestCase):
    def test_legacy_and_output_shape(self):
        x=Ledger(); r=x.apply_batch([event()])
        self.assertEqual(r,[dict(tenant='a',event_id='one',applied=True,balance='10.00')])
        self.assertEqual(x.balance('unknown'),'0.00')

    def test_large_exact_money(self):
        x=Ledger();x.apply_batch([event(amount='9007199254740993.01'),event('two',2,'0.01')])
        self.assertEqual(x.balance('a'),'9007199254740993.02')

    def test_idempotency_original_balance_and_normalized_amount(self):
        x=Ledger();x.apply_batch([event(amount='1'),event('two',2,'5.00')])
        r=x.apply_batch([event(amount='1.00')])
        self.assertEqual(r,[dict(tenant='a',event_id='one',applied=False,balance='1.00')])
        self.assertEqual(x.balance('a'),'6.00')
        x.apply_batch([event('three',3,'1')]);self.assertEqual(x.balance('a'),'7.00')

    def test_duplicate_in_same_batch(self):
        x=Ledger();r=x.apply_batch([event(),event()])
        self.assertEqual([r[0]['applied'],r[1]['applied']],[True,False])
        self.assertEqual(x.balance('a'),'10.00')

    def test_conflict_rolls_back_balance_and_idempotency(self):
        x=Ledger();x.apply_batch([event()])
        with self.assertRaises(ValueError): x.apply_batch([event('two',2,'2'),event(amount='11')])
        self.assertEqual(x.balance('a'),'10.00')
        self.assertTrue(x.apply_batch([event('two',2,'2')])[0]['applied'])

    def test_sequence_replay_and_gaps(self):
        x=Ledger()
        with self.assertRaises(ValueError): x.apply_batch([event(seq=2)])
        x.apply_batch([event()])
        with self.assertRaises(ValueError): x.apply_batch([event('three',3,'1')])
        x.apply_batch([event('two',2,'1')]);self.assertEqual(x.balance('a'),'11.00')

    def test_cross_tenant_atomicity(self):
        x=Ledger()
        with self.assertRaises(ValueError): x.apply_batch([event(),event(tenant='b',amount='-1')])
        self.assertEqual(x.balance('a'),'0.00');self.assertEqual(x.balance('b'),'0.00')
        self.assertTrue(x.apply_batch([event()])[0]['applied'])

    def test_insufficient_funds_rolls_back_all_state(self):
        x=Ledger();x.apply_batch([event(amount='5')])
        with self.assertRaises(ValueError): x.apply_batch([event('two',2,'-3'),event('three',3,'-3')])
        self.assertEqual(x.balance('a'),'5.00')
        x.apply_batch([event('two',2,'-5')]);self.assertEqual(x.balance('a'),'0.00')

    def test_invalid_amounts(self):
        for value in ['NaN','Infinity','1e2','0.001',True,1.2,None]:
            with self.subTest(value=value),self.assertRaises(ValueError): Ledger().apply_batch([event(amount=value)])

    def test_invalid_identity_and_sequence(self):
        for field,value in [('tenant',''),('event_id',' '),('seq',True),('seq',0),('seq','1')]:
            e=event();e[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError): Ledger().apply_batch([e])

    def test_iterator_exception_rollback(self):
        x=Ledger()
        def stream():
            yield event()
            raise RuntimeError('source failed')
        with self.assertRaisesRegex(RuntimeError,'source failed'): x.apply_batch(stream())
        self.assertEqual(x.balance('a'),'0.00')
        self.assertTrue(x.apply_batch([event()])[0]['applied'])

    def test_interleaved_single_pass_and_shared_id(self):
        x=Ledger();r=x.apply_batch(iter([event(),event(tenant='b'),event('two',2,'-1'),event('two',2,'-2',tenant='b')]))
        self.assertEqual([p['balance'] for p in r],['10.00','10.00','9.00','8.00'])

    def test_input_unchanged_and_empty(self):
        x=Ledger();data=[event()];original=copy.deepcopy(data)
        x.apply_batch(data);self.assertEqual(data,original)
        self.assertEqual(x.apply_batch(iter([])),[])


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Acceptance)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    failures=[{'test':str(test),'detail':detail} for test,detail in result.failures+result.errors]
    failed_methods={getattr(test,'test_case',test).id() for test,detail in result.failures+result.errors}
    print(json.dumps({'checks':result.testsRun,'passed':result.testsRun-len(failed_methods),
                      'successful':result.wasSuccessful(),'failures':failures,'log':stream.getvalue()}))
