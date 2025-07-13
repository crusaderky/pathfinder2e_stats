"""Basic dice rolls"""

from __future__ import annotations

import re
from collections.abc import Hashable, Mapping
from typing import cast, overload

import numpy as np
import xarray
from xarray import DataArray

from pathfinder2e_stats.config import get_config, rng

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

    :param int dice:
        Number of dice to roll.
    :param int faces:
        Number of faces on each die.
    :param int bonus:
        Flat bonus/penalty to add to the roll. Default: 0
    :param dims:
        Dimensions to create while rolling, in addition to ``roll``.
        This is a mapping where the keys are the dimension names and the values are the
        number of elements along them.

    Alternatively to `dice`, `faces` and `bonus`, you can pass a single string
    parameter in the format ``XdY``, ``XdY+Z``, or ``XdY-Z``, which means
    *"roll X dice with Y faces each, sum them, then add Z"*.

    :returns:
        A :class:`~xarray.DataArray` containing a random series with the total
        result of the roll, rolled by default 100,000 times, with
        ``dims={"roll": 100_000, **dims}``.

    **Examples:**

    .. only:: doctest

        >>> from pathfinder2e_stats import seed
        >>> seed(0)

    Approximate the mean of 1d6:

    >>> roll("1d6").mean().item()
    3.49798

    Figure out what's the probability to get at least 10 when rolling 2d8+4:

    >>> (roll("2d8+4") >= 10).mean().item()
    0.84486

    Attack three times with a +13 to hit, rolling separately for each attack but
    without increasing MAP:

    >>> roll("d20+13", dims={"target": 3})
    <xarray.DataArray (roll: 100000, target: 3)> Size: 2MB
    array([[23, 18, 20],
           [14, 25, 28],
           [31, 20, 19],
           ...,
           [14, 20, 15],
           [32, 16, 24],
           [19, 31, 22]], shape=(100000, 3))
    Dimensions without coordinates: roll, target

    **See Also:**

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

    roll_size = get_config()["roll_size"]
    raw = DataArray(
        rng().integers(1, faces + 1, size=(roll_size, dice, *dims.values())),
        dims=("roll", "__dice", *dims),
    )
    return cast(DataArray, np.maximum(0, raw.sum("__dice") + bonus))


def d20(
    *,
    fortune: bool | DataArray = False,
    misfortune: bool | DataArray = False,
    dims: Mapping[Hashable, int] | None = None,
) -> DataArray:
    """Roll a d20.

    :param fortune:
        Set to True to roll twice and keep highest. Default: False.
    :param misfortune:
        Set to True to roll twice and keep lowest.
        `fortune` and `misfortune` cancel each other out.
        `fortune` and/or `misfortune` can be :class:`~xarray.DataArray` with
        multiple elements. The result will be broadcasted depending on their dimensions.
        Default: False.
    :param dims:
        Dimensions to create while rolling, in addition to `roll`.
        This is a mapping where the keys are the dimension names and the values are the
        number of elements along them.
    :returns:
        A :class:`~xarray.DataArray` containing a random series with the result of
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

    Attack three times with a +13 to hit and increasing MAP:

    >>> MAP = xarray.DataArray([0, -5, -10], dims=["target"])
    >>> d20(dims={"target": 3}) + 13 + MAP
    <xarray.DataArray (roll: 100000, target: 3)> Size: 2MB
    array([[18, 21, 16],
           [18, 28, 15],
           [29, 24, 22],
           ...,
           [33, 24, 20],
           [19, 21, 17],
           [24, 15, 18]], shape=(100000, 3))
    Dimensions without coordinates: roll, target

    .. note::

        In the last example above, the parameter ``dims={"target": 3}``
        caused to roll separately for each target. Without it, the shape of the
        output array would be the same (due to broadcasting against the ``MAP`` array)
        but on each element along the `roll` dimension there would be a single attack
        roll minus 0, 5, and 10 respectively.
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
