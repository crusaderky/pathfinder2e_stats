from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import numpy as np
from xarray import DataArray, Dataset, where

if TYPE_CHECKING:
    _T = TypeVar("_T", int, DataArray, Dataset)
else:
    # Hack to fix Sphinx rendering
    _T = "int | DataArray | Dataset"


size = 100_000

rng = np.random.default_rng(0)


def seed(n: int) -> None:
    """Seed the library-global random number generator.
    Default is 0, which means that running
    the same code twice will produce identical results.
    """
    global rng  # noqa: PLW0603
    rng = np.random.default_rng(n)


def set_size(n: int) -> int:
    """Set the number of rolls in all simulations. Default is 100,000.
    Returns previous size."""
    global size
    prev, size = size, n
    return prev


def level2rank(level: _T, *, dedication: bool = False) -> _T:
    """Convert a creature's level to their rank, e.g. to determine if they're affected
    by the incapacitation trait or to counteract their abilities. It can also be used
    to determine a spellcaster's maximum spell rank.

    Parameters
    ----------
    level : int
        The creature's level
    dedication : bool, optional
        Set to True to return the highest spell slot rank of a character with caster
        Dedication who took Basic, Expert and Master Spellcasting feats at levels
        4, 12 and 18 respectively.
    """
    if dedication:
        res = where(
            level < 12,
            # FIXME np.clip() raises a DeprecationWarning vs. xarray
            np.maximum(0, np.minimum(3, level // 2 - 1)),
            level // 2 - 2,
        )
        if isinstance(res, np.ndarray) and res.ndim == 0:
            return res.item()  # type: ignore[return-value]
        return res

    return (level + 1) // 2


def rank2level(rank: _T) -> _T:
    """Convert a spell or effect's rank to a creature's maximum level in that rank,
    e.g. the maximum level of a creature that doesn't benefit from the
    incapacitation trait
    """
    return rank * 2
