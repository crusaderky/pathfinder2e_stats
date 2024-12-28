from __future__ import annotations

from typing import Any, Literal, TypeAlias

from xarray import DataArray, concat, where

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
    """Sum bonuses and penalties by type.

    Bonuses of the same type don't stack.
    Penalties of the same type don't stack, but separately from bonuses.
    Untyped bonuses stack.

    Parameters
    ----------
    args : (bonus type, value), ...
        Where bonus type must be one of "untyped", "ability", "circumstance",
        "proficiency", "status", or "item" and value must be an integer or a DataArray.

    Returns
    -------
    Sum of all bonuses and penalties.
    If all values are int, return an int; otherwise return a DataArray.

    Examples
    --------
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

    # This is a bit overcomplicated for the sake of forward compatibility with dask,
    # where we don't know without computing if it's a bonus or penalty
    TMP_DIM = "__bonus_type"
    da = concat(values, dim=TMP_DIM, join="outer", fill_value=0)
    da.coords[TMP_DIM] = btypes

    is_untyped = da.coords[TMP_DIM] == "untyped"
    is_bonus = (da > 0).any(set(da.dims) - {TMP_DIM})

    untyped = where(is_untyped, da, 0)
    bonuses = where(is_bonus & ~is_untyped, da, 0)
    penalties = where(~is_bonus & ~is_untyped, da, 0)
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
