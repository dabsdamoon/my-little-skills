# Ledger design

## Responsibilities
- `domain.py`: pure rules — event validation, exact decimal-string -> integer cents, formatting. No state.
- `repository.py`: owns state (balances, last seq per tenant, idempotency records keyed by `(tenant, event_id)` storing seq, cents and balance-after). `Transaction` stages writes in an overlay.
- `service.py` (`Ledger`): orchestration — parse, idempotency check, sequence check, funds check, stage, commit.

## Atomicity
`apply_batch` reads/writes only through a `Transaction`; later events in the batch see earlier staged ones. `commit()` runs only after the whole iterable is consumed and every event passed, so any ValueError or iterator exception leaves committed state untouched (commit is three dict updates with no validation that can fail).

## Money
Integer cents; no floats, so large values stay exact. Negative amounts are withdrawals; a balance below zero is rejected.

## Likely change: persistent storage
Only `repository.py` changes: `commit()` becomes a database transaction. Domain and service are unaffected. A new rule (e.g. overdraft limits) touches only the funds check in the service/domain.
