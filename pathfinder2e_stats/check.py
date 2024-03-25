from __future__ import annotations

from collections.abc import Hashable, Mapping
from typing import Any, Literal, TypeVar

import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.base import DoS
from pathfinder2e_stats.dice import d20

_Outcome_T = TypeVar("_Outcome_T", DataArray, Dataset)


def map_outcome(
    outcome: _Outcome_T,
    map_: Mapping[DoS | int, DoS | int | bool | DataArray] | None = None,
    /,
    *,
    evasion: bool | DataArray = False,
    juggernaut: bool | DataArray = False,
    resolve: bool | DataArray = False,
    risky_surgery: bool | DataArray = False,
    incapacitation: bool | Literal[-1, 0, 1] | DataArray = 0,
    allow_critical_failure: bool | DataArray = True,
    allow_failure: bool | DataArray = True,
    allow_critical_success: bool | DataArray = True,
) -> _Outcome_T:
    if isinstance(outcome, Dataset):
        outcome = outcome.rename({"outcome": "original_outcome"})
        outcome["outcome"] = map_outcome(
            outcome["original_outcome"],
            map_,
            **{k: v for k, v in locals().items() if k not in ("map_", "outcome")},
        )
        return outcome

    success_to_critical_success = (
        DataArray(evasion)
        | DataArray(juggernaut)
        | DataArray(resolve)
        | DataArray(risky_surgery)
    )
    outcome = outcome.where(
        ~success_to_critical_success | (outcome != DoS.success),
        DoS.critical_success,
    )
    outcome = outcome + incapacitation
    outcome = outcome.clip(
        xarray.where(allow_critical_failure, DoS.critical_failure, DoS.failure),
        xarray.where(allow_critical_success, DoS.critical_success, DoS.success),
    )
    outcome = outcome.where(
        allow_failure | (outcome != DoS.failure),
        DoS.success,
    )

    if map_:
        # False, 0, 0.0, etc.
        dtype = DataArray(next(iter(map_.values()))).dtype
        # Note: avoid changing the same value multiple times!
        return sum(xarray.where(outcome == k, v, 0) for k, v in map_.items()).astype(
            dtype
        )
    return outcome


def check(
    bonus: int | DataArray = 0,
    *,
    DC: int | DataArray,
    keen: bool = False,
    fortune: bool = False,
    misfortune: bool = False,
    hero_point: DoS | int | Literal[False] = False,
    dims: Mapping[Hashable, int] | None = None,
    **kwargs: Any,
) -> Dataset:
    dims = dict(dims) if dims else {}
    if fortune:
        hero_point = False
    elif hero_point is not False:
        dims["hp_reroll"] = 2
        if isinstance(hero_point, int):
            hero_point = DoS(hero_point)

    natural = d20(fortune=fortune, misfortune=misfortune, dims=dims)
    delta = natural + bonus - DC

    assert DoS.failure.value == 0
    assert DoS.success.value == 1
    outcome = (
        (delta <= -10) * DoS.critical_failure
        + ((delta >= 0) & (delta < 10))  # success
        + (delta >= 10) * DoS.critical_success
    )
    del delta

    outcome = (
        outcome.where(natural != 1, outcome - 1)
        .where(natural != 20, outcome + 1)
        .clip(DoS.critical_failure, DoS.critical_success)
    )
    if keen:
        outcome = outcome.where(
            (natural != 19) | (outcome != DoS.success), DoS.critical_success
        )

    ds = Dataset(
        data_vars={
            "bonus": bonus,
            "DC": DC,
            "natural": natural,
            "outcome": outcome,
        },
        attrs={
            "keen": keen,
            **{
                k: v if isinstance(v, (int, bool)) else "varies"
                for k, v in kwargs.items()
            },
            "fortune": fortune,
            "misfortune": misfortune,
            "hero_point": hero_point.name if isinstance(hero_point, DoS) else False,
            "legend": DoS.legend(),
        },
    )
    if hero_point is not False:
        roll0 = outcome.isel(hp_reroll=0, drop=True)
        roll1 = outcome.isel(hp_reroll=1, drop=True)
        use_hero_point = roll0 <= hero_point
        outcome = roll1.where(use_hero_point, roll0)
        ds.update({"outcome": outcome, "use_hero_point": use_hero_point})

    return map_outcome(ds, **kwargs) if kwargs else ds
