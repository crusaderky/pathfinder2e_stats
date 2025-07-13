from typing import TYPE_CHECKING, TypeVar

import xarray
from xarray import DataArray

if TYPE_CHECKING:
    _T = TypeVar("_T", int, DataArray)
else:
    # Hack to fix Sphinx rendering
    _T = "int | DataArray"


def level2rank(level: _T, *, dedication: bool = False) -> _T:
    """Convert a creature's or item's level to their rank, e.g. to determine if they're
    affected by the incapacitation trait or to counteract their abilities. It can also
    be used to determine a spellcaster's maximum spell rank.

    :param level:
        The creature's level
    :param dedication:
        Set to True to return the highest spell slot rank of a character with
        spellcaster Dedication who took Basic, Expert and Master Spellcasting feats at
        levels 4, 12 and 18 respectively. Defaults to False.
    :returns:
        The creature's rank or spellcaster's maximum spell rank.
        Return type matches the type of `level`.
    """
    if dedication:
        res = xarray.where(
            level < 12,
            # FIXME np.clip() raises a DeprecationWarning vs. xarray
            DataArray(level // 2 - 1).clip(0, 3),
            level // 2 - 2,
        )
        return res if isinstance(level, DataArray) else res.item()

    return (level + 1) // 2


def rank2level(rank: _T, *, dedication: bool = False) -> _T:
    """Convert a spell or effect's rank to a creature's or item's maximum level in that
    rank, e.g. the maximum level of a creature that doesn't benefit from the
    incapacitation trait.

    Subtract one to the output for the minimum level in the same rank, or to determine
    the minimum level of a spellcaster in order to be able to cast a spell of a given
    rank.

    :param rank:
        The spell or effect's rank
    :param dedication:
        Set to True to return the level a character with spellcaster Dedication who took
        Basic, Expert and Master Spellcasting feats at levels 4, 12 and 18 respectively
        needs to be to gain a spell slot of this rank. Defaults to False.
    :returns:
        The creature's maximum level within the rank. Return type matches the type of
        `rank`.
    """
    if dedication:
        res = rank * 2 + xarray.where(rank < 4, 2, 4)
        return res if isinstance(rank, DataArray) else res.item()

    return rank * 2
