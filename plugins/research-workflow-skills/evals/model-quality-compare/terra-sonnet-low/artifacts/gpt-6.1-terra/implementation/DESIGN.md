# Ledger design

`domain` validates event fields and converts decimal strings to integer cents;
formatting also stays there. Integer arithmetic keeps money exact without a
floating-point or decimal-context precision limit. `repository` owns the three
in-memory maps: current balances, per-tenant sequence numbers, and event records
(including the balance at application time). `service` orchestrates validation,
idempotency, sequencing, and the nonnegative-balance rule.

A batch operates on a shallow copy of all three maps. Their keys and values are
immutable, so no shared mutable entries can leak changes. Only after the input
iterator is exhausted successfully is the snapshot installed. Validation,
insufficient funds, or an iterator exception therefore leaves all original
maps unchanged, including idempotency records. Replays consult the snapshot, so
repeats within a batch work the same way as repeats across batches.

A future persistent or concurrent implementation would need a repository
transaction with isolation and an atomic commit instead of copying and replacing
maps; concurrent calls are not synchronized by this in-memory implementation.
The domain validation and the observable batch semantics should remain unchanged.
