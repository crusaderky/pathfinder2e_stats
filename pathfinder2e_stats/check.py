from __future__ import annotations

from collections.abc import Hashable, Mapping
from typing import Any, Literal

import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.damage_spec import DoS
from pathfinder2e_stats.dice import d20


def map_outcomes(
    map_: Mapping[DoS | int, DoS | int] | None = None,
    /,
    *,
    evasion: bool = False,
    juggernaut: bool = False,
    resolve: bool = False,
    risky_surgery: bool = False,
    incapacitation: bool | Literal[-1, 0, 1] = 0,
    allow_critical_failure: bool = True,
    allow_failure: bool = True,
    allow_critical_success: bool = True,
) -> dict[DoS, DoS]:
    out = {
        DoS(k) if isinstance(k, int) else k: DoS(v) if isinstance(v, int) else v
        for k, v in (map_ or {}).items()
    }
    if evasion or juggernaut or resolve or risky_surgery:
        out[DoS.success] = DoS.critical_success

    if incapacitation == -1:
        out.update(
            {
                DoS.critical_success: DoS.success,
                DoS.success: DoS.failure,
                DoS.failure: DoS.critical_failure,
            }
        )
    elif incapacitation in (True, 1):
        out.update(
            {
                DoS.critical_failure: DoS.failure,
                DoS.failure: DoS.success,
                DoS.success: DoS.critical_success,
            }
        )

    if not allow_failure:
        for k, v in out.items():
            if v in (DoS.failure, DoS.critical_failure):
                out[k] = DoS.success
        out[DoS.critical_failure] = DoS.success
        out[DoS.failure] = DoS.success
    elif not allow_critical_failure:
        for k, v in out.items():
            if v is DoS.critical_failure:
                out[k] = DoS.failure
        out[DoS.critical_failure] = DoS.failure
    if not allow_critical_success:
        for k, v in out.items():
            if v is DoS.critical_success:
                out[k] = DoS.success
        out[DoS.critical_success] = DoS.success

    return {k: v for k, v in out.items() if k != v}


# Work around name shadowing
_map_outcomes_func = map_outcomes


def check(
    bonus: int | DataArray = 0,
    *,
    DC: int | DataArray,
    map_outcomes: Mapping[DoS | int, DoS | int] | None = None,
    keen: bool = False,
    fortune: bool = False,
    misfortune: bool = False,
    hero_point: DoS | int | Literal[False] = False,
    dims: Mapping[Hashable, int] | None = None,
    **kwargs: Any,
) -> Dataset:
    map_ = _map_outcomes_func(map_outcomes, **kwargs)

    dims = dict(dims) if dims else {}
    if fortune:
        hero_point = False
    elif hero_point is not False:
        dims["hp_reroll"] = 2
        if isinstance(hero_point, int):
            hero_point = DoS(hero_point)

    natural = d20(fortune=fortune, misfortune=misfortune, dims=dims)
    delta = natural + bonus - DC
    natural = natural.astype("i1")

    assert DoS.failure.value == 0
    assert DoS.success.value == 1
    outcome = (
        (delta <= -10) * DoS.critical_failure
        + ((delta >= 0) & (delta < 10))  # success
        + (delta >= 10) * DoS.critical_success
    ).astype("i1")
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

    if map_:
        # Some mappings are needed
        # Note: avoid changing the same value multiple times!
        map2 = {k: map_.get(k, k) for k in DoS if map_.get(k, k)}
        if map2:
            outcome = sum(xarray.where(outcome == k, v, 0) for k, v in map2.items())
        else:  # Edge case: map everything to failure
            outcome = xarray.zeros_like(outcome)

    ds = Dataset(
        data_vars={
            "bonus": bonus,
            "DC": DC,
            "natural": natural,
            "outcome": outcome,
        },
        attrs={
            "keen": keen,
            "fortune": fortune,
            "misfortune": misfortune,
            "hero_point": hero_point.name if isinstance(hero_point, DoS) else False,
            "map_outcomes": {k.name: v.name for k, v in map_.items()},
            "legend": {dos.value: dos.name for dos in DoS},
        },
    )
    if hero_point is not False:
        roll0 = outcome.isel(hp_reroll=0, drop=True)
        roll1 = outcome.isel(hp_reroll=1, drop=True)
        use_hero_point = roll0 <= hero_point
        outcome = roll1.where(use_hero_point, roll0)
        ds.update({"outcome": outcome, "use_hero_point": use_hero_point})
    return ds
