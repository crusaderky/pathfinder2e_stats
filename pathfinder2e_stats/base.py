from __future__ import annotations

from enum import IntEnum

size = 100_000


def set_size(n: int) -> int:
    """Set the number of rolls in all simulations. Default is 100,000.
    Returns previous size."""
    global size
    prev, size = size, n
    return prev


class DoS(IntEnum):
    no_roll = -2
    critical_failure = -1
    failure = 0
    success = 1
    critical_success = 2
