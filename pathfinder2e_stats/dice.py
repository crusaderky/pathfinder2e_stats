"""Basic dice rolls"""

from __future__ import annotations

import re
from collections.abc import Hashable, Mapping
from typing import cast, overload

import numpy as np
import xarray
from xarray import DataArray

from pathfinder2e_stats import base

# XdY+Z | XdY-Z | dY+Z | dY-Z | dY
_pattern = re.compile(r"([0-9]+)?d([0-9]+)([+-][0-9]+)?$")


@overload
def roll(s: str, /, *, dims: Mapping[Hashable, int] | None = None) -> DataArray: ...


@overload
def roll(
    dice: int,
    faces: int,
    bonus: int = 0,
    /,
    *,
    dims: Mapping[Hashable, int] | None = None,
) -> DataArray: ...


def roll(
    dice_or_s: int | str,
    faces: int | None = None,
    bonus: int = 0,
    /,
    *,
    dims: Mapping[Hashable, int] | None = None,
) -> DataArray:
    if isinstance(dice_or_s, str):
        if faces is not None or bonus != 0:
            raise TypeError(
                "dice() accepts either a single string compact parameter or "
                "disaggregated numerical ones"
            )
        m = _pattern.match(dice_or_s.strip())
        if not m:
            raise ValueError(f"Could not parse dice roll: {dice_or_s!r}")
        dice = int(m.group(1)) if m.group(1) else 1
        faces = int(m.group(2))
        bonus = int(m.group(3)) if m.group(3) else 0
    else:
        dice = dice_or_s
        if faces is None:
            raise TypeError("roll() missing 1 required positional argument: 'faces'")

    if dims is None:
        dims = {}

    raw = DataArray(
        base.rng.integers(1, faces + 1, size=(base.size, dice, *dims.values())),
        dims=("roll", "count", *dims),
    )
    return cast(DataArray, np.maximum(0, raw.sum("count") + bonus))


def d20(
    *,
    fortune: bool | DataArray = False,
    misfortune: bool | DataArray = False,
    dims: Mapping[Hashable, int] | None = None,
) -> DataArray:
    if fortune is False and misfortune is False:
        return roll(1, 20, dims=dims)

    fortune = DataArray(fortune)
    misfortune = DataArray(misfortune)
    dims = dict(dims) if dims else {}
    dims["__fortune"] = 2
    raw = roll(1, 20, dims=dims)
    return xarray.where(
        fortune & ~misfortune,
        raw.max("__fortune"),
        xarray.where(
            misfortune & ~fortune,
            raw.min("__fortune"),
            raw.isel(__fortune=0),
        ),
    )
