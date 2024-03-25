from __future__ import annotations

from typing import Literal, TypeAlias

from xarray import DataArray, concat

BonusType: TypeAlias = Literal[
    "untyped",
    "circumstance",
    "proficiency",
    "status",
    "item",
]
_BONUS_DOMAIN = {"untyped", "circumstance", "proficiency", "status", "item"}


def sum_bonuses(*args: tuple[BonusType, int | DataArray]) -> DataArray:
    if not args:
        return DataArray(0)

    btypes = []
    values = []
    for btype, value in args:
        if btype not in _BONUS_DOMAIN:
            raise ValueError(f"Expected one of {list(_BONUS_DOMAIN)}; got {btype}")
        btypes.append(btype)
        values.append(DataArray(value) if isinstance(value, int) else value)

    if len(values) == 1:
        return values[0]

    # This is a bit overcomplicated for the sake of forward-compatibility with the dask
    # backend, where we don't know without computing if it's a bonus or penalty
    TEMPDIM = "__bonus_type__"
    da: DataArray = concat(values, dim=TEMPDIM, join="outer", fill_value=0)
    da.coords[TEMPDIM] = btypes

    is_untyped = da.coords[TEMPDIM] == "untyped"
    is_bonus = (da > 0).any(set(da.dims) - {TEMPDIM})

    untyped = da.where(is_untyped, 0)
    bonuses = da.where(is_bonus & ~is_untyped, 0)
    penalties = da.where(~is_bonus & ~is_untyped, 0)
    return (
        untyped.sum(TEMPDIM)
        + bonuses.groupby(TEMPDIM).max().sum(TEMPDIM)
        + penalties.groupby(TEMPDIM).min().sum(TEMPDIM)
    )
