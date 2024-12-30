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

    **See also:**
    :func:`check`
    :func:`map_outcome`
    """

    no_roll = -2
    critical_failure = -1
    failure = 0
    success = 1
    critical_success = 2

    def __str__(self) -> str:
        return self.name.replace("_", " ").capitalize()


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
    """Roll a d20 and compare the result to a Difficulty Class (DC).

    This can be used to simulate an attack roll, skill check, saving throw, etc. -
    basically anything other than a damage roll (but see :func:`damage`).

    :param bonus: The bonus or penalty to add to the d20 roll.
    :param DC: The Difficulty Class to compare the result to.
    :param keen: Set to True to Strike with a weapon inscribed with a `Keen rune`_.
        Attacks with this weapon are a critical hit on a 19 on the die as long as that
        result is a success. This property has no effect on a 19 if the result would be
        a failure. Default: False.
    :param fortune: Set to True to roll twice and keep highest, e.g. when under the
        effect of `Sure Strike`_. Default: False.
    :param misfortune: Set to True to roll twice and keep lowest, e.g. when under the
        effect of `Ill Omen`_. Default: False.
        Fortune and misfortune cancel each other out.
    :param hero_point: Set to a :class:`DoS` value to spend a hero point if the outcome
        is equal to or less than the given value. e.g.
        ``hero_point=DoS.critical_failure`` rerolls only critical failures, whereas
        ``hero_point=DoS.failure`` rerolls anything less than a success.
        Hero points are a fortune effect, so they can't be used when fortune is True.
    :param dims: Additional dimensions to create while rolling, in addition to ``roll``.
        This is a mapping where the keys are the dimension names and the values are the
        number of elements along them.
    :param kwargs: If kwargs are specified, call :func:`map_outcome` before returning
        the output.

    :returns: A :class:`xarray.Dataset` containing the following variables:

        - ``bonus``: As the parameter
        - ``DC``: As the parameter
        - ``natural``: The result of the natural d20 roll before adding the bonus
        - ``use_hero_point``: Whether a hero point was used to reroll the outcome.
        - ``original_outcome``: The outcome of the check before any modifications
          by :func:`map_outcome`. Only present if any parameters to the function
          are specified.
        - ``outcome``: The final outcome of the check

        All data variables other than ``outcome`` are only returned for the purpose of
        debugging and data tracking. For the same reason, ``attrs`` contains a wealth
        of useful information regarding the check.

    **All inputs can be either scalars or** :class:`xarray.DataArray`.
    Providing array inputs will cause all the outputs to be broadcasted accordingly.

    **Examples:**

    Strike an enemy with AC18 with a +10 weapon::

        >>> check(10, DC=18)
        <xarray.Dataset> Size: 2MB
        Dimensions:  (roll: 100000)
        Dimensions without coordinates: roll
        Data variables:
            bonus    int64 8B 10
            DC       int64 8B 18
            natural  (roll) int64 800kB 10 12 3 19 9 5 1 19 12 ... 7 6 2 2 16 5 12 10 11
            outcome  (roll) int64 800kB 1 1 0 2 1 0 -1 2 1 1 1 ... 1 0 0 0 0 0 1 0 1 1 1
        Attributes:
            keen:        False
            fortune:     False
            misfortune:  False
            hero_point:  False
            legend:      {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'Su...

    Strike three times in sequence, with MAP, and test how it works out differently
    against a henchman with AC16 or a boss with AC20::

        >>> MAP = xarray.DataArray([0, -5, -10], dims=["strike"])
        >>> targets = xarray.DataArray(
        ...     [16, 20],
        ...     dims=["target"],
        ...     coords={"target": ["henchman", "boss"]})
        >>> check(10 + MAP, DC = targets, dims=MAP.sizes)
        <xarray.Dataset> Size: 7MB
        Dimensions:  (strike: 3, target: 2, roll: 100000)
        Coordinates:
        * target   (target) <U4 32B 'henchman' 'boss'
        Dimensions without coordinates: strike, roll
        Data variables:
            bonus    (strike) int64 24B 10 5 0
            DC       (target) int64 16B 16 20
            natural  (roll, strike) int64 2MB 1 20 11 18 5 7 19 3 ... 14 15 11 12 4 5 15
            outcome  (roll, strike, target) int64 5MB -1 -1 2 2 0 0 2 ... 0 0 0 0 -1 0 0

    Note the parameter ``dims=MAP.sizes``. This causes :func:`check` to roll
    independently for each value of MAP, but to reuse the same roll against different
    targets. This is reflected by the dimensionality of the ``natural`` and the
    ``outcome`` arrays.

    Study the roll above::

        >>> c = pf2.check(10 + MAP, DC = targets)
        >>> (
        ...     pf2.outcome_counts(c)
        ...     .stack(row=["target", "strike"])
        ...     .round(2).T.to_pandas() * 100.0
        ... )
        outcome        Critical success  Success  Failure  Critical failure
        target strike
        mook   0                   25.0     50.0     20.0               5.0
               1                    5.0     44.9     45.2               4.9
               2                    5.1     19.9     45.1              29.9
        boss   0                    5.1     49.9     40.0               5.0
               1                    5.0     25.0     45.0              25.0
               2                    5.1      0.0     45.2              49.8

    Roll a DC20 reflex save with a +12 bonus, evasion (which converts a success into a
    critical success), and spend a hero point on failure or critical failure::

        >>> c = check(12, DC=20, hero_point=DoS.failure, evasion=True)
        >>> outcome_counts(c).to_pandas()
        outcome
        Critical success    0.87726
        Failure             0.10500
        Critical failure    0.01774
        >>> c.use_hero_point.value_counts("roll", normalize=True).to_pandas()
        unique_value
        False    0.64898
        True     0.35102

    .. _Keen rune: https://2e.aonprd.com/Equipment.aspx?ID=2843
    .. _Sure Strike: https://2e.aonprd.com/Spells.aspx?ID=1709
    .. _Ill Omen: https://2e.aonprd.com/Spells.aspx?ID=1566
    """
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

    outcome = xarray.where(natural == 1, outcome - 1, outcome)
    outcome = xarray.where(natural == 20, outcome + 1, outcome)
    outcome = outcome.clip(DoS.critical_failure, DoS.critical_success)

    outcome = xarray.where(
        DataArray(keen) & (natural == 19) & (outcome == DoS.success),
        DoS.critical_success,
        outcome,
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
                else "varies"
                if isinstance(hero_point, DataArray)
                else False
            ),
            "legend": {dos.value: str(dos) for dos in DoS.__members__.values()},
        },
    )
    if hero_point is not False:
        roll0 = outcome.isel(hp_reroll=0)
        roll1 = outcome.isel(hp_reroll=1)
        # Can't use a hero point when there's already a fortune effect
        use_hero_point = (roll0 <= hero_point) & ~DataArray(fortune)
        outcome = xarray.where(use_hero_point, roll1, roll0)
        ds.update({"outcome": outcome, "use_hero_point": use_hero_point})

    return map_outcome(ds, **kwargs) if kwargs else ds


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
    incapacitation: bool | DataArray = False,
    allow_critical_failure: bool | DataArray = True,
    allow_failure: bool | DataArray = True,
    allow_critical_success: bool | DataArray = True,
) -> _Outcome_T:
    """Convert the output of :func:`check` following a set of rules.

    This function is typically called indirectly, through the keyword arguments of
    :func:`check`.

    :param outcome: Either the :class:`xarray.Dataset` returned by :func:`check` or just
        its ``outcome`` variable
    :param map_: An arbitrary ``{from: to, ...}`` or ``[(from, to), ...]`` mapping of
        outcomes. Both from and to must be :class:`DoS` values or their int equivalents.
        This is applied *after* all other rules. Default: no bespoke mapping.
    :param evasion: Set to True to convert a success into a critical success.
        Default: False.

        .. note::

            This is a catch-all parameter for any equivalent class feature or feat,
            such as juggernaut, bravery, risky surgery, etc. Each class has a different
            name for them, most times purely for the sake of flavour.

    :param incapacitation: Set to True when an incapacitation effect is applied to
       a creature whose level is more than twice the effect rank. If True, all
       outcomes are improved by one notch. Default: False.

       See also :func:`level2rank` and :func:`rank2level`.
    :param allow_critical_failure: Set to False if there is no critical failure effect.
        If False, all critical failures are mapped to simple failures.
        Default: True.
    :param allow_failure: Set to False if there is no failure effect.
        If False, all failures will be mapped to success. Default: True.
    :param allow_critical_success: Set to False if there is no critical
        success effect. If False, all critical successes will be mapped to simple
        successes. Default: True.
    :returns: If ``outcome`` is the :class:`xarray.Dataset` returned by :func:`check`,
        return a shallow copy of it with the ``outcome`` variable replaced and the
        previous outcome stored in ``original_outcome``.
        If ``outcome`` is a :class:`xarray.DataArray`, return a new DataArray with
        the mapped outcomes.

    **All parameters can either be scalars or** :class:`xarray.DataArray`.

    **Examples:**

    Cast a 5th rank `Calm`_ spell (DC30) and catch in the area three targets:

    - A level 8 creature;
    - A level 11 creature, who therefore benefits from the spell's incapacitation
      trait;
    - A level 9 cleric, who benefits from the *Resolute Faith* class feature::

        >>> spell_rank = 5
        >>> targets = xarray.Dataset({
        ...     "level": ("target", [8, 11, 9]),
        ...     "bonus": ("target", [16, 21, 24]),
        ...     "evasion": ("target", [False, False, True])})
        >>> check(targets.bonus,
        ...       DC=30,
        ...       dims=targets.sizes,  # targets rolls independently
        ...       evasion=targets.evasion,
        ...       incapacitation=rank2level(spell_rank) < targets.level)

    .. _Calm: https://2e.aonprd.com/Spells.aspx?ID=1458
    """
    if isinstance(outcome, Dataset):
        outcome = outcome.rename({"outcome": "original_outcome"})
        outcome["outcome"] = map_outcome(
            outcome["original_outcome"],
            map_,
            **{k: v for k, v in locals().items() if k not in ("map_", "outcome")},
        )
        return outcome

    success_to_critical_success = DataArray(evasion)
    orig_outcome = outcome
    outcome = xarray.where(
        success_to_critical_success & (outcome == DoS.success),
        DoS.critical_success,
        outcome,
    )
    outcome = outcome + incapacitation
    outcome = outcome.clip(
        xarray.where(allow_critical_failure, DoS.critical_failure, DoS.failure),
        xarray.where(allow_critical_success, DoS.critical_success, DoS.success),
    )
    outcome = xarray.where(orig_outcome == DoS.no_roll, orig_outcome, outcome)
    outcome = xarray.where(
        allow_failure | (outcome != DoS.failure),
        outcome,
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


def outcome_counts(
    outcome: DataArray | Dataset,
    dim: Hashable = "roll",
    *,
    new_dim: Hashable = "outcome",
    normalize: bool = True,
) -> DataArray:
    """Count the occurrences of each outcome in a check.

    :param outcome: Either the :class:`xarray.Dataset` returned by :func:`check` or
        :func:`map_outcome` or just their ``outcome`` variable.
    :param dim: The dimension to reduce when counting the outcomes.
        Default: ``roll``.
    :param new_dim: The name of the new dimension containing all
        outcome values. Default: ``outcome``.
        The new dimension is sorted from critical success to critical failure and
        contains only the values that actually occurred.
    :param normalize: If True, normalize the counts so that they add
        up to 1. If False, return the raw counts. Default: True.
    :returns:
        A :class:`xarray.DataArray` containing the counts of each outcome, with
        the same dimensions as the input, minus ``dim``, plus ``new_dim``.

    **See also:**
    `value_counts`_

    **Examples:**
    ::

        >>> outcome_counts(check(12, DC=20))
        <xarray.DataArray 'outcome' (outcome: 4)> Size: 32B
        array([0.14827, 0.50276, 0.29844, 0.05053])
        Coordinates:
        * outcome  (outcome) <U16 256B 'Critical success' ... 'Critical failure'
    """
    if isinstance(outcome, Dataset):
        outcome = outcome.outcome

    # Use accessor installed in pathfinder2e_stats.accessors
    vc = outcome.value_counts(dim, new_dim=new_dim, normalize=normalize)
    vc.coords[new_dim] = [str(DoS(i)) for i in vc.coords[new_dim]]
    # Sort from critical success to critical failure
    return vc.isel({new_dim: slice(None, None, -1)})
