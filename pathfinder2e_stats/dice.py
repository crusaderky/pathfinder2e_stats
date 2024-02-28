"""Basic dice rolls"""
from __future__ import annotations

import re
from collections.abc import Hashable
from typing import cast, overload

import numpy as np
from xarray import DataArray

from pathfinder2e_stats import base

# XdY+Z | XdY-Z | dY+Z | dY-Z | dY
_pattern = re.compile(r"([0-9]+)?d([0-9]+)([+-][0-9]+)?$")


@overload
def roll(s: str, /, *, dims: dict[Hashable, int] | None = None) -> DataArray:
    ...


@overload
def roll(
    count: int,
    faces: int,
    bonus: int = 0,
    /,
    *,
    dims: dict[Hashable, int] | None = None,
) -> DataArray:
    ...


def roll(
    count_or_s: int | str,
    faces: int | None = None,
    bonus: int = 0,
    /,
    *,
    dims: dict[Hashable, int] | None = None,
) -> DataArray:
    if isinstance(count_or_s, str):
        if faces is not None or bonus != 0:
            raise TypeError(
                "dice() accepts either a single string compact parameter or "
                "disaggregated numerical ones"
            )
        m = _pattern.match(count_or_s.strip())
        if not m:
            raise ValueError(f"Could not parse dice roll: {count_or_s!r}")
        count = int(m.group(1)) if m.group(1) else 1
        faces = int(m.group(2))
        bonus = int(m.group(3)) if m.group(3) else 0
    else:
        count = count_or_s
        if faces is None:
            raise TypeError("roll() missing 1 required positional argument: 'faces'")

    if dims is None:
        dims = {}

    raw = DataArray(
        np.random.randint(1, faces + 1, size=(base.size, count, *dims.values())),
        dims=("roll", "count", *dims),
    )
    return cast(DataArray, np.maximum(0, raw.sum("count") + bonus))


def d20(
    *,
    fortune: bool = False,
    misfortune: bool = False,
    dims: dict[Hashable, int] | None = None,
) -> DataArray:
    dims = dims.copy() if dims else {}
    if fortune and misfortune:
        raise ValueError("Can't have both fortune and misfortune on a roll")
    if fortune or misfortune:
        dims["__fortune"] = 2
        raw = roll(1, 20, dims=dims)
        return raw.max("__fortune") if fortune else raw.min("__fortune")
    else:
        return roll(1, 20, dims=dims)
