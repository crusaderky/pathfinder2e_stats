from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.dice import d20

if TYPE_CHECKING:
    _Outcome_T = TypeVar("_Outcome_T", DataArray, Dataset)
else:
    # Hack to fix Sphinx rendering
    _Outcome_T = "DataArray | Dataset"


class DoS(IntEnum):
    """Enum for all possible check outcomes. In order to improve readability and
    reduce human error, you should not use the numeric values directly.

    ===== ================
    value code
    ===== ================
       -2 no_roll
       -1 critical_failure
        0 failure
        1 success
        2 critical_success
    ===== ================

    Disequality comparisons work as expected. For example,
    ``mycheck.outcome >= DoS.success`` returns True for success and critical success.
    """

    no_roll = -2
    critical_failure = -1
    failure = 0
    success = 1
    critical_success = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").capitalize()


def map_outcome(
    outcome: _Outcome_T,
    map_: (
        Mapping[DoS | int | DataArray, object]
        | Iterable[tuple[DoS | int | DataArray, object]]
        | None
    ) = None,
    /,
    *,
    evasion: bool | DataArray = False,
    juggernaut: bool | DataArray = False,
    resolve: bool | DataArray = False,
    risky_surgery: bool | DataArray = False,
    incapacitation: bool | int | DataArray = 0,
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
    orig_outcome = outcome
    outcome = outcome.where(
        ~success_to_critical_success | (outcome != DoS.success),
        DoS.critical_success,
    )
    outcome = outcome + incapacitation
    outcome = outcome.clip(
        xarray.where(allow_critical_failure, DoS.critical_failure, DoS.failure),
        xarray.where(allow_critical_success, DoS.critical_success, DoS.success),
    )
    outcome = orig_outcome.where(orig_outcome == DoS.no_roll, outcome)
    outcome = outcome.where(
        allow_failure | (outcome != DoS.failure),
        DoS.success,
    )

    if map_ is not None:
        if isinstance(map_, Mapping):
            map_ = map_.items()
        map_ = list(map_)
        if not map_:
            return xarray.zeros_like(outcome)

        # False, 0, 0.0, etc.
        out = DataArray(0).astype(DataArray(map_[0][1]).dtype)
        if out.dtype.kind == "U":
            out = DataArray("")
        for from_, to in reversed(map_):
            out = xarray.where(outcome == from_, to, out)
        return out

    return outcome


def check(
    bonus: int | DataArray = 0,
    *,
    DC: int | DataArray,
    keen: bool | DataArray = False,
    fortune: bool | DataArray = False,
    misfortune: bool | DataArray = False,
    hero_point: DoS | int | Literal[False] | DataArray = False,
    dims: Mapping[Hashable, int] | None = None,
    **kwargs: Any,
) -> Dataset:
    dims = dict(dims) if dims else {}
    if hero_point is not False:
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

    outcome = outcome.where(
        ~DataArray(keen) | (natural != 19) | (outcome != DoS.success),
        DoS.critical_success,
    )

    ds = Dataset(
        data_vars={
            "bonus": bonus,
            "DC": DC,
            "natural": natural,
            "outcome": outcome,
        },
        attrs={
            "keen": keen if isinstance(keen, bool) else "varies",
            **{
                k: v if isinstance(v, int | bool) else "varies"
                for k, v in kwargs.items()
            },
            "fortune": fortune if isinstance(fortune, bool) else "varies",
            "misfortune": misfortune if isinstance(misfortune, bool) else "varies",
            "hero_point": (
                hero_point.name
                if isinstance(hero_point, DoS)
                else "varies" if isinstance(hero_point, DataArray) else False
            ),
            "legend": {dos.value: str(dos) for dos in DoS.__members__.values()},
        },
    )
    if hero_point is not False:
        roll0 = outcome.isel(hp_reroll=0)
        roll1 = outcome.isel(hp_reroll=1)
        # Can't use a hero point when there's already a fortune effect
        use_hero_point = (roll0 <= hero_point) & ~DataArray(fortune)
        outcome = roll1.where(use_hero_point, roll0)
        ds.update({"outcome": outcome, "use_hero_point": use_hero_point})

    return map_outcome(ds, **kwargs) if kwargs else ds


def outcome_counts(
    check_outcome: DataArray | Dataset,
    dim: Hashable = "roll",
    *,
    new_dim: Hashable = "outcome",
    normalize: bool = True,
) -> DataArray:
    if isinstance(check_outcome, Dataset):
        check_outcome = check_outcome.outcome

    vc = check_outcome.value_counts(dim, new_dim=new_dim, normalize=normalize)
    vc.coords[new_dim] = [str(DoS(i)) for i in vc.coords[new_dim]]
    # Sort from critical success to critical failure
    vc = vc.isel({new_dim: slice(None, None, -1)})
    return vc
