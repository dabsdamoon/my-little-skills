"""Validation and exact money conversion at the ledger boundary."""

import re
from decimal import Decimal


_PLAIN_DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]{0,2})?|\.[0-9]{1,2})')


def amount(value):
    """Normalize a plain decimal string to integer cents."""
    if not isinstance(value, str) or not _PLAIN_DECIMAL.fullmatch(value):
        raise ValueError('amount must be a plain decimal string with at most two decimal places')
    whole, _, fraction = value.partition('.')
    # Convert without Decimal arithmetic (which would use the ambient context)
    # or a direct string-to-int conversion (which can have a digit limit).
    return int(Decimal(whole + fraction.ljust(2, '0')))


def format_balance(cents):
    whole, fraction = divmod(cents, 100)
    return f'{Decimal(whole):f}.{fraction:02d}'


def validate_event(event):
    if not isinstance(event, dict):
        raise ValueError('event must be a dictionary')
    tenant = event.get('tenant')
    event_id = event.get('event_id')
    seq = event.get('seq')
    for name, value in (('tenant', tenant), ('event_id', event_id)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name} must be a nonblank string')
    if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
        raise ValueError('seq must be a positive integer')
    return tenant, event_id, seq, amount(event.get('amount'))
