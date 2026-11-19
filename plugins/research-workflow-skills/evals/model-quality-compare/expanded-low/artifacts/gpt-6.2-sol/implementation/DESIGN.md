# Ledger design

The domain module validates event fields and converts monetary strings to
integer cents. Arithmetic uses integers, independent of floating-point precision
and the active decimal context. Tenant and event IDs are checked for blankness
but otherwise retained as supplied.

The repository owns current per-tenant sequence and balance, plus immutable
event records keyed by tenant and event ID. It looks up replays before checking
sequence continuity so old events can return their original post-event balances.
The service consumes the iterable once and assembles the public response.

Each batch starts with shallow copies of the repository's maps. Their values
are immutable, so staged writes cannot leak into committed state. Later events
in the same batch see earlier staged writes. The service replaces the committed
state only after iteration and response construction finish successfully. Any
exception propagates without publishing the draft. This is batch atomicity for
serial calls, not a guarantee of thread-safe concurrent writes.

Copying the maps costs time and memory proportional to retained state, even
for a small batch. If persistence becomes necessary, the repository can store
accounts and event records in a database with a unique tenant/event-ID key.
The service would replace copying and publishing with a transaction that
commits after iterator exhaustion; the validation and response shape could
remain unchanged. Concurrent writers would also need transactional protection
around the per-tenant sequence and balance checks.
