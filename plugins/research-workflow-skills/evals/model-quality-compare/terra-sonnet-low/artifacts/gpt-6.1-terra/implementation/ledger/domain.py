"""Validation and exact money conversion for ledger events."""
import re

_AMOUNT = re.compile(r'[+-]?[0-9]+(?:\.[0-9]{1,2})?\Z')


def amount(value):
    """Parse a plain decimal string into integer cents."""
    if not isinstance(value, str) or not _AMOUNT.fullmatch(value):
        raise ValueError('amount must be a plain decimal string with at most two decimal places')
    negative = value.startswith('-')
    unsigned = value.lstrip('+-')
    whole, _, fraction = unsigned.partition('.')
    cents = int(whole) * 100 + int((fraction + '00')[:2])
    return -cents if negative else cents


def format_amount(cents):
    sign = '-' if cents < 0 else ''
    cents = abs(cents)
    return f'{sign}{cents // 100}.{cents % 100:02d}'


def validate_event(event):
    if not isinstance(event, dict):
        raise ValueError('event must be a dictionary')
    tenant = event.get('tenant')
    event_id = event.get('event_id')
    seq = event.get('seq')
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError('tenant must be a nonblank string')
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError('event_id must be a nonblank string')
    if isinstance(seq, bool) or not isinstance(seq, int) or seq <= 0:
        raise ValueError('seq must be a positive integer')
    return tenant, event_id, seq, amount(event.get('amount'))
