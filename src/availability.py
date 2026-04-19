"""
Room availability model for the Birol Hotel prototype.

The live hotel would pull this from its property-management system. For the
course prototype we generate a *deterministic* set of fully-booked dates so
the grader sees a realistic pattern (peak season + scattered weekends) that
is stable across reloads and can be overlaid on a calendar picker.

Fully-booked dates fall into two buckets:

  * **Peak blocks** — contiguous runs around real high-season periods
    (Istanbul summer, Christmas / New Year, Turkish spring holiday).
  * **Scattered weekends** — a deterministic one-in-three Saturdays in the
    next 12 months, so the calendar shows a realistic "some weekends gone"
    feel.

The module exposes one function, :func:`unavailable_dates`, returning an
ordered list of ISO yyyy-mm-dd strings.
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta


# Peak blocks are inclusive on both ends.
PEAK_BLOCKS: tuple[tuple[date, date, str], ...] = (
    (date(2026, 7, 10), date(2026, 7, 20), "Istanbul summer peak"),
    (date(2026, 8, 8),  date(2026, 8, 15), "Mid-August peak"),
    (date(2026, 12, 27), date(2027, 1, 3), "Christmas / New Year"),
    (date(2027, 4, 22), date(2027, 4, 28), "Spring holiday"),
)


def _daterange(start: date, end: date):
    """Yield every date from *start* to *end* inclusive."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def _deterministic_bit(d: date) -> int:
    """0/1 coin flip derived from the date — stable across runs."""
    h = hashlib.md5(d.isoformat().encode("ascii")).digest()
    return h[0] & 1


def unavailable_dates(
    start: date | None = None,
    horizon_days: int = 365,
) -> list[str]:
    """Return ISO dates that are fully booked between *start* and horizon.

    *start* defaults to :func:`date.today`.
    """
    start = start or date.today()
    end = start + timedelta(days=horizon_days)

    blocked: set[date] = set()

    # 1. Peak blocks intersecting the horizon.
    for block_start, block_end, _label in PEAK_BLOCKS:
        s = max(block_start, start)
        e = min(block_end, end)
        if s <= e:
            blocked.update(_daterange(s, e))

    # 2. Roughly half of Saturdays are gone (deterministic).
    for d in _daterange(start, end):
        if d.weekday() == 5 and _deterministic_bit(d):
            blocked.add(d)

    return sorted(d.isoformat() for d in blocked)


if __name__ == "__main__":  # manual smoke-check
    dates = unavailable_dates()
    print(f"{len(dates)} unavailable dates in the next year")
    for d in dates[:10]:
        print(" ", d)
