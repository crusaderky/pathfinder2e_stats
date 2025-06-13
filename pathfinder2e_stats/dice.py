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
    """Roll the given number of dice with the given number of faces, sum them up,
    and add an optional flat bonus/penalty.

    :param dice: Number of dice to roll.
    :param faces: Number of faces on each die.
    :param bonus: Flat bonus/penalty to add to the roll. Default: 0
    :param dims: Dimensions to create while rolling, in addition to ``roll``.
        This is a mapping where the keys are the dimension names and the values are the
        number of elements along them.

    Alternatively to ``dice``, ``faces`` and ``bonus``, you can pass a single string
    parameter in the format ``XdY``, ``XdY+Z``, or ``XdY-Z``, which means
    *"roll X dice with Y faces each, sum them, then add Z"*.

    :returns: A :class:`xarray.DataArray` containing a random series with the total
        result of the roll, rolled by default 100,000 times, with
        ``dims={"roll": 100_000, **dims}``.

    **Examples:**

    .. only:: doctest

        >>> from pathfinder2e_stats import seed
        >>> seed(0)

    Approximate the mean of 2d8+4:

    >>> roll("2d8+4").mean().item()
    12.9984

    Attack three different targets with a +13 to hit, rolling separately for each but
    without increasing the MAP between them:

    >>> roll(1, 20, 13, dims={"target": 3})
    <xarray.DataArray (roll: 100000, target: 3)> Size: 2MB
    array([[18, 26, 26],
           [18, 33, 25],
           [29, 29, 32],
           ...,
           [33, 29, 30],
           [19, 26, 27],
           [24, 20, 28]], shape=(100000, 3))
    Dimensions without coordinates: roll, target

    **See Also:**

    - :func:`seed`
    - :func:`set_size`
    - :func:`d20`
    - :func:`check`
    """
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
        base.rng().integers(1, faces + 1, size=(base.size, dice, *dims.values())),
        dims=("roll", "count", *dims),
    )
    return cast(DataArray, np.maximum(0, raw.sum("count") + bonus))


def d20(
    *,
    fortune: bool | DataArray = False,
    misfortune: bool | DataArray = False,
    dims: Mapping[Hashable, int] | None = None,
) -> DataArray:
    """Roll a d20.

    :param fortune: if True, roll twice and keep highest.
    :param misfortune: if True, roll twice and keep lowest.
        fortune and misfortune cancel each other out.
        ``fortune`` and/or ``misfortune`` can be :class:`xarray.DataArray` with
        multiple elements. The result will be broadcasted depending on their dimensions.
    :param dims: Dimensions to create while rolling, in addition to ``roll``.
        This is a mapping where the keys are the dimension names and the values are the
        number of elements along them.
    :returns: A :class:`xarray.DataArray` containing a random series with the result of
        the d20 roll.

    **Examples:**

    .. only:: doctest

        >>> from pathfinder2e_stats import seed
        >>> seed(0)

    Measure the effect of Sure Strike on the mean of an attack roll:

    >>> sure_strike = xarray.DataArray(
    ...     [False, True], dims=["Sure Strike"],
    ...     coords={"Sure Strike": [False, True]},
    ... )
    >>> d20(fortune=sure_strike).mean("roll").to_pandas()
    Sure Strike
    False    10.50545
    True     13.83809
    dtype: float64

    Attack 3 targets, with increasing MAP:

    >>> MAP = xarray.DataArray([0, -5, -10], dims=["target"])
    >>> d20(dims={"target": 3}) + MAP
    <xarray.DataArray (roll: 100000, target: 3)> Size: 2MB
    array([[ 5,  8,  3],
           [ 5, 15,  2],
           [16, 11,  9],
           ...,
           [20, 11,  7],
           [ 6,  8,  4],
           [11,  2,  5]], shape=(100000, 3))
    Dimensions without coordinates: roll, target

    .. note::

        In the last example above, the parameter ``dims={"target": 3}``
        caused to roll separately for each target. Without it, the shape of the
        output array would be the same (due to broadcasting against the MAP array)
        but on each element of the series there would be a single attack roll minus
        0, 5, and 10 respectively.
    """
    if fortune is True and misfortune is True:
        return roll(1, 20, dims=dims)
    if fortune is False and misfortune is False:
        return roll(1, 20, dims=dims)

    fortune = DataArray(fortune)
    misfortune = DataArray(misfortune)
    dims = dict(dims) if dims else {}
    dims["__fortune"] = 2
    raw = roll(1, 20, dims=dims)
    return xarray.where(
        fortune & ~misfortune,
        raw.max("__fortune"),  # roll with fortune
        xarray.where(
            misfortune & ~fortune,
            raw.min("__fortune"),  # roll with misfortune
            raw.isel(__fortune=0),  # roll normally (disregard second roll)
        ),
    )
