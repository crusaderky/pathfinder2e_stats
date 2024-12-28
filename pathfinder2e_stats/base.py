from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import numpy as np
import xarray
from xarray import DataArray

if TYPE_CHECKING:
    _T = TypeVar("_T", int, DataArray)
else:
    # Hack to fix Sphinx rendering
    _T = "int | DataArray"


size = 100_000

rng = np.random.default_rng(0)


def seed(n: int) -> None:
    """Seed the library-global random number generator.

    Default is 0, which means that running the same code twice will produce
    identical results.
    """
    global rng  # noqa: PLW0603
    rng = np.random.default_rng(n)


def set_size(n: int) -> int:
    """Set the number of rolls in all simulations. Default is 100,000.
    Returns previous size."""
    global size
    prev, size = size, n
    return prev


def _maybe_unwrap_scalar(x: DataArray | np.ndarray | np.generic) -> Any:
    if (isinstance(x, np.ndarray) and x.ndim == 0) or isinstance(x, np.generic):
        return x.item()
    return x


def level2rank(level: _T, *, dedication: bool = False) -> _T:
    """Convert a creature's level to their rank, e.g. to determine if they're affected
    by the incapacitation trait or to counteract their abilities. It can also be used
    to determine a spellcaster's maximum spell rank.

    :param level:
        The creature's level
    :param dedication:
        Set to True to return the highest spell slot rank of a character with
        spellcaster Dedication who took Basic, Expert and Master Spellcasting feats at
        levels 4, 12 and 18 respectively. Defaults to False.
    :returns:
        The creature's rank or spellcaster's maximum spell rank.
        Return type matches the type of ``level``.
    """
    if dedication:
        res = xarray.where(
            level < 12,
            # FIXME np.clip() raises a DeprecationWarning vs. xarray
            np.maximum(0, np.minimum(3, level // 2 - 1)),
            level // 2 - 2,
        )
        return _maybe_unwrap_scalar(res)

    return (level + 1) // 2


def rank2level(rank: _T, *, dedication: bool = False) -> _T:
    """Convert a spell or effect's rank to a creature's maximum level in that rank,
    e.g. the maximum level of a creature that doesn't benefit from the
    incapacitation trait.

    Subtract one to the output for the minimum level in the same rank, or to determine
    the minimum level of a spellcaster in order to be able to cast a spell of a given
    rank.

    :param rank:
        The spell or effect's rank
    :param dedication:
        Set to True to return the level a character with spellcaster
        Dedication who took Basic, Expert and Master Spellcasting feats at levels
        4, 12 and 18 respectively needs to be to gain a spell slot of this rank.
        Defaults to False.
    :returns:
        The creature's maximum level within the rank.
        Return type matches the type of ``rank``.
    """
    if dedication:
        res = rank * 2 + xarray.where(rank < 4, 2, 4)
        return _maybe_unwrap_scalar(res)

    return rank * 2
