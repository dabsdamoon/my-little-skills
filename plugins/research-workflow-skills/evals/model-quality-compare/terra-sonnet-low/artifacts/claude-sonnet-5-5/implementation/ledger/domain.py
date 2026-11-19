"""Pure domain rules: event validation and money formatting. No state."""
import re

_AMOUNT = re.compile(r'-?(\d+)(?:\.(\d{1,2}))?\Z')


def parse_event(event):
    """Return (tenant, event_id, seq, cents) or raise ValueError."""
    if not isinstance(event, dict):
        raise ValueError('event must be a dict')
    tenant, event_id = event.get('tenant'), event.get('event_id')
    for name, v in (('tenant', tenant), ('event_id', event_id)):
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f'invalid {name}')
    seq = event.get('seq')
    if type(seq) is not int or seq < 1:
        raise ValueError('invalid seq')
    return tenant, event_id, seq, cents(event.get('amount'))


def cents(value):
    if not isinstance(value, str) or not value.isascii():
        raise ValueError('invalid amount')
    m = _AMOUNT.match(value)
    if not m:
        raise ValueError('invalid amount')
    total = int(m.group(1)) * 100 + int((m.group(2) or '0').ljust(2, '0'))
    return -total if value.startswith('-') else total


def format_cents(n):
    sign = '-' if n < 0 else ''
    q, r = divmod(abs(n), 100)
    return f'{sign}{q}.{r:02d}'
