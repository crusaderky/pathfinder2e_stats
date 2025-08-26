from __future__ import annotations

from collections.abc import Collection, Hashable, Iterable, Mapping
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import numpy as np
import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.dice import d20
from pathfinder2e_stats.tools import _parse_independent_dependent_dims

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
    independent_dims: Mapping[Hashable, int | None] | Collection[Hashable] = (),
    dependent_dims: Collection[Hashable] = (),
    keen: bool | DataArray = False,
    perfected_form: bool | DataArray = False,
    fortune: bool | DataArray = False,
    misfortune: bool | DataArray = False,
    hero_point: DoS | int | Literal[False] | DataArray = False,
    evasion: bool | DataArray = False,
    incapacitation: bool | Literal[-1, 0, 1] | DataArray = False,
    allow_critical_failure: bool | DataArray = True,
    allow_failure: bool | DataArray = True,
    allow_critical_success: bool | DataArray = True,
    primary_target: DataArray | Dataset | None = None,
) -> Dataset:
    """Roll a d20 and compare the result to a Difficulty Class (DC).

    This can be used to simulate an attack roll, skill check, saving throw, etc. -
    basically anything other than a damage roll (but see :func:`damage`).

    All parameters can be either scalars or :class:`~xarray.DataArray`.
    Providing array parameters will cause all the outputs to be broadcasted accordingly.

    .. only:: doctest

        >>> from pathfinder2e_stats import seed, set_config
        >>> seed(0)

    :param bonus:
        The bonus or penalty to add to the d20 roll.
    :param DC:
        The Difficulty Class to compare the result to.
    :param independent_dims:
        Dimensions along which to roll independently for each point.

        This can be either a mapping where the keys are the dimension names and
        the values are the number of elements along them, or a collection of a
        subset of the dimensions of any of the input parameters.

        You may also mix dimensions that already exist in the input parameters with new
        dimensions in a mapping; the values for the already existing dimensions will be
        ignored.

        Dimension `roll` is always independent and must not be included.

        See examples below.

    :param dependent_dims:
        Dimensions along which there must be a single dice roll for all points.
        They must be a subset of the dimensions of the input parameters.
        `independent_dims` plus `dependent_dims` must cover all dimensions of the input
        parameters. The name of these two parameters comes from the concept in
        statistics of dependent and independent variables.

        **Global configuration**

        `independent_dims` and `depedent_dims` add to config keys
        `check_independent_dims` and `check_dependent_dims` respectively.
        If a dimension is always going to be independent or dependent throughout your
        workflow, you can avoid specifying it every time:

        Instead of:

        >>> check(10, DC=DC,
        ...       independent_dims=["x"],
        ...       dependent_dims=["y"])  # doctest: +SKIP

        You can write:
        >>> set_config(check_independent_dims=["x"], check_dependent_dims=["y"])
        >>> check(10, DC=DC)  # doctest: +SKIP

    .. only:: doctest

        >>> set_config(check_independent_dims=(), check_dependent_dims=())

    :param keen:
        Set to True to Strike with a weapon inscribed with a
        :prd_equipment:`Keen <2843>` rune.
        Attacks with this weapon are a critical hit on a 19 on the die as long as that
        result is a success. This property has no effect on a 19 if the result would be
        a failure. Default: False.
    :param perfected_form:
        Level 19 monk feature. On your first Strike of your turn, if
        you roll lower than 10, you can treat the attack roll as a 10.
        This is a fortune effect. Disabled when fortune=True. Default: False.
    :param fortune:
        Set to True to roll twice and keep highest, e.g. when under the
        effect of :prd_spells:`Sure Strike <1709>`. Default: False.
    :param misfortune:
        Set to True to roll twice and keep lowest, e.g. when under the
        effect of :prd_spells:`Ill Omen <1566>`. Default: False.
        Fortune and misfortune cancel each other out.
    :param hero_point:
        Set to a :class:`DoS` value to spend a hero point if the outcome
        is equal to or less than the given value. e.g.
        ``hero_point=DoS.critical_failure`` rerolls only critical failures, whereas
        ``hero_point=DoS.failure`` rerolls anything less than a success.
        Hero points are a fortune effect, so they can't be used when fortune is True.
    :param evasion:
        Passed to :func:`map_outcome` post-processing.
    :param incapacitation:
        Passed to :func:`map_outcome` post-processing.
    :param allow_critical_failure:
        Passed to :func:`map_outcome` post-processing.
    :param allow_failure:
        Passed to :func:`map_outcome` post-processing.
    :param allow_critical_success:
        Passed to :func:`map_outcome` post-processing.
    :param primary_target:
        Passed to :func:`map_outcome` post-processing.
    :returns:
        A :class:`~xarray.Dataset` containing the following variables:

        bonus, etc.
            As the parameter. Only present when not the default value.
        natural
            The result of the natural d20 roll before adding the bonus
        use_hero_point
            Whether a hero point was used to reroll the outcome.
            Only present if `hero_point` is not False.
        original_outcome
            The outcome of the check before any modifications by :func:`map_outcome`.
            Only present if any parameters to the function are specified.
        outcome
            The final outcome of the check

    **Examples:**

    Strike an enemy with AC18 with a +10 weapon:

    >>> check(10, DC=18)
    <xarray.Dataset> Size: 2MB
    Dimensions:  (roll: 100000)
    Dimensions without coordinates: roll
    Data variables:
        bonus    int64 8B 10
        DC       int64 8B 18
        natural  (roll) int64 800kB 18 13 11 6 7 1 2 1 4 17 ... 8 4 15 3 14 13 1 1 4
        outcome  (roll) int64 800kB 2 1 1 0 0 -1 0 -1 0 1 ... -1 1 0 1 0 1 1 -1 -1 0
    Attributes:
        legend:   {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'Succe...

    Strike three times in sequence, with MAP, and test how the same strike
    works out differently against a henchman with AC16 or a boss with AC20:

    >>> MAP = DataArray([0, -5, -10], dims=["action"])
    >>> targets = DataArray([16, 20], coords={"target": ["henchman", "boss"]})
    >>> outcome = check(10 + MAP, DC = targets,
    ...                 independent_dims=["action"],
    ...                 dependent_dims=["target"])
    >>> outcome
    <xarray.Dataset> Size: 7MB
    Dimensions:  (action: 3, target: 2, roll: 100000)
    Coordinates:
      * target   (target) <U8 64B 'henchman' 'boss'
    Dimensions without coordinates: action, roll
    Data variables:
        bonus    (action) int64 24B 10 5 0
        DC       (target) int64 16B 16 20
        natural  (roll, action) int64 2MB 10 12 3 19 9 5 1 19 ... 6 2 15 2 4 15 11 9
        outcome  (roll, action, target) int64 5MB 1 1 1 0 -1 -1 2 ... 1 1 1 0 0 -1
    Attributes:
        legend:   {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'Succe...

    Note the parameters ``independent_dims`` and ``dependent_dims``. They cause
    :func:`check` to roll independently for each value of MAP, but to reuse the same
    roll against different targets.
    This is reflected by the dimensionality of the `natural` and the `outcome` arrays.

    Study the roll above:

    >>> (
    ...     outcome_counts(outcome)
    ...     .stack(row=["target", "action"])
    ...     .round(2).T.to_pandas() * 100.0
    ... )
    outcome          Critical success  Success  Failure  Critical failure
    target   action
    henchman 0                   25.0     50.0     20.0               5.0
             1                    5.0     45.0     45.0               5.0
             2                    5.0     20.0     45.0              30.0
    boss     0                    5.0     50.0     40.0               5.0
             1                    5.0     25.0     45.0              25.0
             2                    5.0      0.0     45.0              50.0

    Roll a DC20 reflex save with a +12 bonus, evasion (which converts a success into a
    critical success), and spend a hero point on failure or critical failure:

    >>> c = check(12, DC=20, hero_point=DoS.failure, evasion=True)
    >>> outcome_counts(c).to_pandas()
    outcome
    Critical success    0.87786
    Failure             0.10424
    Critical failure    0.01790
    Name: outcome, dtype: float64
    >>> c.use_hero_point.value_counts("roll", normalize=True).to_pandas()
    unique_value
    False    0.6524
    True     0.3476
    Name: use_hero_point, dtype: float64
    """
    # Create output dataset, normalize input args, and collect input dimensions
    ds = Dataset(
        data_vars={"bonus": bonus, "DC": DC},
        attrs={"legend": {dos.value: str(dos) for dos in DoS.__members__.values()}},
    )
    for k, v, default in (
        ("keen", keen, False),
        ("perfected_form", perfected_form, False),
        ("fortune", fortune, False),
        ("misfortune", misfortune, False),
        ("hero_point", hero_point, False),
        ("evasion", evasion, False),
        ("incapacitation", incapacitation, False),
        ("allow_critical_failure", allow_critical_failure, True),
        ("allow_failure", allow_failure, True),
        ("allow_critical_success", allow_critical_success, True),
        ("primary_target", primary_target, None),
    ):
        if v is not default:
            if k == "primary_target" and isinstance(v, Dataset):
                v = v.outcome
            ds[k] = v

    # Normalize and validate independent_dims and dependent_dims
    independent_dims = _parse_independent_dependent_dims(
        "check", ds, independent_dims, dependent_dims
    )

    hp_reroll_coord = ["original"]
    if perfected_form is not False:
        independent_dims["hp_reroll"] = 2
        hp_reroll_coord.append("perfected form")
    if hero_point is not False:
        independent_dims["hp_reroll"] = independent_dims.get("hp_reroll", 1) + 1
        hp_reroll_coord.append("hero point")

    natural = d20(fortune=fortune, misfortune=misfortune, dims=independent_dims)
    if len(hp_reroll_coord) > 1:
        natural.coords["hp_reroll"] = hp_reroll_coord
    if perfected_form is not False:
        natural = xarray.where(
            natural.coords["hp_reroll"] == "perfected form", 10, natural
        )
    ds["natural"] = natural

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
    ds["outcome"] = outcome

    if hero_point is not False or perfected_form is not False:
        # Hero point, Perfected Form and fortune effects that apply before the roll
        # (e.g. Sure Strike) are mutually exclusive.
        nfortune = ~DataArray(fortune)

        cur_outcome = outcome.sel(hp_reroll="original", drop=True)
        if perfected_form is not False:
            use_perfected_form = DataArray(perfected_form) & nfortune
            pf_outcome = outcome.sel(hp_reroll="perfected form", drop=True)
            cur_outcome = xarray.where(
                use_perfected_form,
                np.maximum(pf_outcome, cur_outcome),
                cur_outcome,
            )

        if hero_point is not False:
            use_hero_point = (cur_outcome <= hero_point) & nfortune
            hp_outcome = outcome.sel(hp_reroll="hero point", drop=True)
            cur_outcome = xarray.where(use_hero_point, hp_outcome, cur_outcome)
            ds["use_hero_point"] = use_hero_point

        ds["outcome"] = cur_outcome
    assert "hp_reroll" not in ds["outcome"].dims

    return map_outcome(
        ds,
        evasion=evasion,
        incapacitation=incapacitation,
        allow_critical_failure=allow_critical_failure,
        allow_failure=allow_failure,
        allow_critical_success=allow_critical_success,
        primary_target=primary_target,
    )


def map_outcome(
    outcome: _Outcome_T,
    map_: (
        Mapping[DoS | int | DataArray, Any]
        | Iterable[tuple[DoS | int | DataArray, Any]]
        | None
    ) = None,
    /,
    *,
    evasion: bool | DataArray = False,
    incapacitation: bool | Literal[-1, 0, 1] | DataArray = False,
    allow_critical_failure: bool | DataArray = True,
    allow_failure: bool | DataArray = True,
    allow_critical_success: bool | DataArray = True,
    primary_target: DataArray | Dataset | None = None,
) -> _Outcome_T:
    """Convert the output of :func:`check` following a set of rules.

    This function is typically called indirectly, through the keyword arguments of
    :func:`check`.

    All parameters can either be scalars or :class:`~xarray.DataArray`.

    .. only:: doctest

        >>> from pathfinder2e_stats import rank2level, seed, Damage, damage
        >>> seed(0)

    :param outcome:
        Either the :class:`~xarray.Dataset` returned by :func:`check` or
        just its `outcome` variable.
    :param map_:
        An arbitrary ``{from: to, ...}`` mapping or ``[(from, to), ...]`` sequence of
        tuples of outcomes. `from` must be :class:`DoS` values or their int equivalents.
        `to` can be anything, including other dtypes such as strings.
        This is applied *after* all other rules.
        Any DoS value not in `from` is mapped to the null value by default.
        Default: no bespoke mapping.
    :param evasion:
        Set to True to convert a success into a critical success. Default: False.

        .. note::

            This is a catch-all parameter for any equivalent class feature or feat,
            such as juggernaut, bravery, risky surgery, etc. Each class has a different
            name for them, most times purely for the sake of flavour.

    :param incapacitation:
        Set to True when an incapacitation effect is applied to
        a creature whose level is more than twice the effect rank. If 1 or True, all
        outcomes are improved by one notch (use this for the creature's saving throws).
        If -1, all outcomes are worsened by one notch (use this for checks against the
        creature). Default: False.

        See also :func:`level2rank` and :func:`rank2level`.
    :param allow_critical_failure:
        Set to False if there is no critical failure effect.
        If False, all critical failures are mapped to simple failures. Default: True.
    :param allow_failure:
        Set to False if there is no failure effect.
        If False, all failures will be mapped to success. Default: True.
    :param allow_critical_success:
        Set to False if there is no critical success effect. If False, all critical
        successes will be mapped to simple successes. Default: True.
    :param primary_target:
        Starfinder :srd_classes:`Soldier <5-soldier>` class feature.
        Use this to map the outcome of the saving throw against Area Fire or Auto-Fire
        vs. the outcome of the Primary Target Strike. A target hit by the Primary Target
        Strike downgrades simple successes on the saving throw vs. Area Fire and
        Auto-Fire to failures. The value of this parameter must be a Dataset as
        returned by :func:`check`, or a DataArray of degrees of success of the Primary
        Target Strike (as the ``outcome`` variable of such Dataset).

        Example:

        >>> weapon = Damage("piercing", 1, 10)  # Stellar Cannon
        >>> primary_target = damage(check(6, DC=15), weapon)  # atk +6 vs. AC15
        >>> area_fire = damage(
        ...     # Basic reflex save vs. class DC + tracking
        ...     check(5, DC=18, primary_target=primary_target),
        ...     weapon.copy(basic_save=True),
        ... )

    :returns:
        If `outcome` is the :class:`~xarray.Dataset` returned by :func:`check`,
        return a shallow copy of it with the `outcome` variable replaced and the
        previous outcome stored in `original_outcome`.
        If `outcome` is a :class:`~xarray.DataArray`, return a new DataArray with
        the mapped outcomes.
        If `map_` is defined, the dtype of the return value will be the dtype of
        the values of `map_`; otherwise it will be int like the input.

    **Examples:**

    Cast a 5th rank :prd_spells:`Calm <1458>` spell (DC30) and catch in the
    area three targets:

    - A level 8 creature;
    - A level 11 creature, who therefore benefits from the spell's incapacitation
      trait;
    - A level 9 cleric, who benefits from the *Resolute Faith* class feature:

      >>> spell_rank = 5
      >>> targets = xarray.Dataset({
      ...     "level": ("target", [8, 11, 9]),
      ...     "bonus": ("target", [16, 21, 24]),
      ...     "evasion": ("target", [False, False, True])})
      >>> check(targets.bonus,
      ...       DC=30,
      ...       independent_dims=["target"],
      ...       evasion=targets.evasion,
      ...       incapacitation=rank2level(spell_rank) < targets.level)
      <xarray.Dataset> Size: 7MB
      Dimensions:           (target: 3, roll: 100000)
      Dimensions without coordinates: target, roll
      Data variables:
          bonus             (target) int64 24B 16 21 24
          DC                int64 8B 30
          evasion           (target) bool 3B False False True
          incapacitation    (target) bool 3B False True False
          natural           (roll, target) int64 2MB 18 6 4 6 12 15 ... 11 16 14 8 8 6
          original_outcome  (roll, target) int64 2MB 1 0 0 0 1 1 1 1 ... 1 0 1 1 0 0 1
          outcome           (roll, target) int64 2MB 1 1 0 0 2 2 1 2 ... 2 0 2 2 0 1 2
      Attributes:
          legend:   {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'Succe...
    """
    if isinstance(outcome, Dataset):
        ds = outcome
        changed = map_ is not None
        ds = ds.rename({"outcome": "original_outcome"})
        for k, v, default in (
            ("evasion", evasion, False),
            ("incapacitation", incapacitation, False),
            ("allow_critical_failure", allow_critical_failure, True),
            ("allow_failure", allow_failure, True),
            ("allow_critical_success", allow_critical_success, True),
            ("primary_target", primary_target, None),
        ):
            if v is not default:
                changed = True
                # Note: when map_outcome is a tail call from check, this is redundant.
                if k == "primary_target" and isinstance(v, Dataset):
                    v = v.outcome
                ds[k] = v
        if not changed:
            return outcome
        # FIXME how do we display map_ in the data variables?
        ds["outcome"] = map_outcome(
            ds["original_outcome"],
            map_,
            evasion=evasion,
            incapacitation=incapacitation,
            allow_critical_failure=allow_critical_failure,
            allow_failure=allow_failure,
            allow_critical_success=allow_critical_success,
            primary_target=primary_target,
        )
        return ds

    orig_outcome = outcome
    outcome = xarray.where(
        evasion & (outcome == DoS.success),
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
    if primary_target is not None:
        if isinstance(primary_target, Dataset):
            primary_target = primary_target.outcome
        outcome = xarray.where(
            (primary_target >= DoS.success) & (outcome == DoS.success),
            DoS.failure,
            outcome,
        )

    if map_ is None:
        return outcome

    if isinstance(map_, Mapping):
        map_ = map_.items()
    norm_map = [
        # Preserve dtype promotion in result_type
        # e.g. int + np.int8 -> np.int8
        # However, we need to wrap str objects and such, which
        # np.result_type does not understand.
        (from_, to if isinstance(to, int | float | bool) else DataArray(to))
        for from_, to in map_
    ]
    dtype = np.result_type(*(v for _, v in norm_map)) if norm_map else np.dtype(int)
    if dtype.kind in "TU":
        out = xarray.full_like(outcome, fill_value="", dtype=dtype)
    else:
        out = xarray.zeros_like(outcome, dtype=dtype)

    # In case of multiple matches, leftmost wins.
    for from_, to in reversed(norm_map):
        out = xarray.where(outcome == from_, to, out)
    return out


def outcome_counts(
    outcome: DataArray | Dataset,
    dim: Hashable = "roll",
    *,
    new_dim: Hashable = "outcome",
    normalize: bool = True,
) -> DataArray:
    """Count the occurrences of each outcome in a check.

    :param outcome:
        Either the :class:`~xarray.Dataset` returned by :func:`check` or
        :func:`map_outcome` or just their ``outcome`` variable.
    :param dim:
        The dimension to reduce when counting the outcomes.
        Default: ``roll``.
    :param new_dim:
        The name of the new dimension containing all
        outcome values. Default: ``outcome``.
        The new dimension is sorted from critical success to critical failure and
        contains only the values that actually occurred.
    :param normalize:
        If True, normalize the counts so that they add
        up to 1. If False, return the raw counts. Default: True.
    :returns:
        A :class:`~xarray.DataArray` containing the counts of each outcome, with
        the same dimensions as the input, minus `dim`, plus `new_dim`.

    **See also:**
    `value_counts`_

    **Examples:**

    .. only:: doctest

        >>> from pathfinder2e_stats import seed
        >>> seed(0)

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
