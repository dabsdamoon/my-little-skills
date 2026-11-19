"""Validation and exact money representation, independent of stored state."""
from dataclasses import dataclass
import re


_DECIMAL = re.compile(r'[+-]?[0-9]+(?:\.[0-9]{1,2})?\Z')


def amount(value):
    """Parse a plain decimal string into integer cents (without rounding)."""
    if not isinstance(value, str) or not _DECIMAL.fullmatch(value):
        raise ValueError('amount must be a plain decimal string with at most two places')
    negative = value.startswith('-')
    unsigned = value.lstrip('+-')
    whole, _, fraction = unsigned.partition('.')
    cents = int(whole) * 100 + int(fraction.ljust(2, '0'))
    return -cents if negative else cents


def format_money(cents):
    sign = '-' if cents < 0 else ''
    whole, fraction = divmod(abs(cents), 100)
    return f'{sign}{whole}.{fraction:02d}'


@dataclass(frozen=True)
class Event:
    tenant: str
    event_id: str
    seq: int
    cents: int

    @classmethod
    def parse(cls, raw):
        if not isinstance(raw, dict):
            raise ValueError('event must be a dictionary')
        tenant, event_id = raw.get('tenant'), raw.get('event_id')
        if any(not isinstance(value, str) or not value.strip()
               for value in (tenant, event_id)):
            raise ValueError('tenant and event_id must be nonblank strings')
        seq = raw.get('seq')
        if isinstance(seq, bool) or not isinstance(seq, int) or seq <= 0:
            raise ValueError('seq must be a positive integer')
        return cls(tenant, event_id, seq, amount(raw.get('amount')))
