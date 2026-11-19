# Ledger design

`domain.py` validates event shapes and decimal syntax and converts money to integer
cents. No floating-point or context-limited decimal arithmetic is involved. Names
are validated but preserved exactly; amounts normalize by numeric cents, including
signed zero. Decimal strings have digits before the optional decimal point and
one or two digits after it; an optional leading sign is supported.

`repository.py` owns balances, last sequences, and immutable original receipts.
`service.py` enforces sequencing, idempotency and nonnegative balances and builds
public responses. A replay reads the receipt's original balance, not today's.

Each batch shallow-copies the three state dictionaries. Their values are integers
or immutable receipts, so staged changes cannot leak into committed state. Only
successful exhaustion of the single-pass input commits the staged state by one
reference replacement. Validation failures, conflicts, overdrafts and iterator
exceptions all discard the snapshot. Inputs are never modified. This trades
O(total stored state) copying per batch for simple, auditable atomicity.

This is an in-memory, synchronous API, not a concurrent or durable database.
A future durable backend would replace snapshot copying with a database
transaction covering balances, sequences and receipts, with a unique constraint
on (tenant, event_id) and serialization of each tenant's updates. Domain parsing
and public response behavior could remain unchanged; transaction orchestration
would need to move behind a repository transaction boundary.
