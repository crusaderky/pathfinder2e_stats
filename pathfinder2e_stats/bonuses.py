from __future__ import annotations

from typing import Any, Literal, TypeAlias

import xarray
from xarray import DataArray

BonusType: TypeAlias = Literal[
    "untyped",
    "ability",
    "circumstance",
    "proficiency",
    "status",
    "item",
]
_BONUS_DOMAIN = frozenset(BonusType.__args__)  # type: ignore[attr-defined]


def sum_bonuses(*args: tuple[BonusType, int | DataArray]) -> Any:
    """Sum bonuses and penalties by type to calculate the total bonus/penalty.

    Bonuses of the same type don't stack.
    Penalties of the same type don't stack, but bonuses and penalties of the
    same type subtract from each other.
    Untyped bonuses and penalties always stack.

    :param \\*args:
        ``(bonus type, value), ...``, where bonus type must be one of:

        - ``untyped``
        - ``ability``
        - ``circumstance``
        - ``proficiency``
        - ``status``
        - ``item``

        and value must be an integer or a :class:`~xarray.DataArray`.

    :returns:
        Sum of all bonuses and penalties.
        If all values are int, return an int; otherwise return a
        :class:`~xarray.DataArray`.

    **Examples**:

    >>> sum_bonuses(("status", 1), ("status", 2), ("circumstance", 3))
    5
    """
    if not args:
        return 0

    btypes = []
    values = []
    for btype, value in args:
        if btype not in _BONUS_DOMAIN:
            raise ValueError(f"Expected one of {list(_BONUS_DOMAIN)}; got {btype}")
        btypes.append(btype)
        values.append(DataArray(value) if isinstance(value, int) else value)

    # Special case needed for older xarray versions
    if len(args) == 1:
        return args[0][1]

    # This is a bit overcomplicated for the sake of forward compatibility with dask,
    # where we don't know without computing if it's a bonus or penalty
    TMP_DIM = "__bonus_type"
    da = xarray.concat(values, dim=TMP_DIM, join="outer", fill_value=0)
    da.coords[TMP_DIM] = btypes

    is_untyped = da.coords[TMP_DIM] == "untyped"
    is_bonus = (da > 0).any(set(da.dims) - {TMP_DIM})

    untyped = xarray.where(is_untyped, da, 0)
    bonuses = xarray.where(is_bonus & ~is_untyped, da, 0)
    penalties = xarray.where(~is_bonus & ~is_untyped, da, 0)
    res = (
        untyped.sum(TMP_DIM)
        + bonuses.groupby(TMP_DIM).max().sum(TMP_DIM)
        + penalties.groupby(TMP_DIM).min().sum(TMP_DIM)
    )

    if any(isinstance(value, DataArray) for _, value in args):
        return res

    assert res.ndim == 0
    assert not res.coords
    assert not res.attrs
    return res.values.item()
