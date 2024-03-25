from __future__ import annotations

from enum import IntEnum
from typing import TypeVar

from xarray import DataArray, Dataset

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

    def __str__(self) -> str:
        return self.name.replace("_", " ").capitalize()

    @classmethod
    def legend(cls) -> dict[int, str]:
        return {dos.value: str(dos) for dos in cls.__members__.values()}


_T = TypeVar("_T", int, DataArray, Dataset)


def level2rank(level: _T) -> _T:
    """Convert a creature's level to their rank, e.g. to determine if they're affected
    by the incapacitation trait or to counteract their abilities
    """
    return (level + 1) // 2


def rank2level(rank: _T) -> _T:
    """Convert a spell or effect's rank to a creature's maximum level in that rank,
    e.g. the maximum level of a creature that doesn't benefit from the
    incapacitation trait
    """
    return rank * 2
