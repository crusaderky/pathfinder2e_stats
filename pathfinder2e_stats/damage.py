from __future__ import annotations

from collections.abc import Collection, Hashable, Mapping
from typing import cast

import numpy as np
import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.check import check
from pathfinder2e_stats.damage_spec import Damage, DamageLike, ExpandedDamage
from pathfinder2e_stats.dice import roll
from pathfinder2e_stats.tools import _parse_independent_dependent_dims


def damage(
    check_outcome: Dataset,
    damage_spec: DamageLike,
    *,
    independent_dims: Collection[Hashable] = (),
    dependent_dims: Collection[Hashable] = (),
    weaknesses: Mapping[str, int] | DataArray | None = None,
    resistances: Mapping[str, int] | DataArray | None = None,
    immunities: Mapping[str, bool] | Collection[str] | DataArray | None = None,
    persistent_damage_rounds: int = 3,
    persistent_damage_DC: int | Mapping[str, int] | DataArray = 15,
    splash_damage_targets: int = 2,
) -> Dataset:
    """Roll for damage.

    .. only:: doctest

        >>> from pathfinder2e_stats import seed, set_config
        >>> seed(0)

    :param check_outcome:
        The outcome of the check that caused the damage.
        This must be the return value of :func:`check`, typically either
        for an attack roll or for a saving throw (but it could also be
        a skill check).
    :param damage_spec:
        The damage specification to use for rolling damage.
        This must be a :class:`~pathfinder2e_stats.Damage`,
        :class:`~pathfinder2e_stats.ExpandedDamage`, a
        dict representing an :class:`~pathfinder2e_stats.ExpandedDamage`, or
        a combination thereof using the `+` operator.
    :param independent_dims:
        Dimensions along which to roll independently for each point.

        This must be a subset of the dimensions of any of the input parameters.
        Note that a dimension may be:

        - independent in both :func:`check` and :func:`damage`; e.g. two
          iterative Strikes;
        - independent in :func:`check`, but dependent in :func:`damage`;
          e.g. multiple targets roll a check to save vs.
          :prd_spells:`Fireball <1530>`, damage rolled only once;
        - dependent  in both :func:`check` and :func:`damage`, e.g.
          :prd_feats:`Swipe <4795>` vs. two targets, or a what-if analysis of
          the same strike vs. two different targets or from two different attackers.

        Dimensions `roll` and `damage_type` are always independent and must not be
        included.

        See examples below.
    :param dependent_dims:
        Dimensions along which there must be a single dice roll for all points.

        See :func:`check` for more details.

        **Global configuration**

        `independent_dims` and `depedent_dims` add to config keys
        `damage_independent_dims` and `damage_dependent_dims` respectively.
        If a dimension is always going to be independent or dependent throughout your
        workflow, you can avoid specifying it every time:

        Instead of:

        >>> damage(check_outcome, spec,
        ...        independent_dims=["x"],
        ...        dependent_dims=["y"])  # doctest: +SKIP

        You can write:
        >>> set_config(damage_independent_dims=["x"], damage_dependent_dims=["y"])
        >>> damage(check_outcome, spec)  # doctest: +SKIP

        .. only:: doctest

            >>> set_config(damage_independent_dims=(), damage_dependent_dims=())

    :param weaknesses:
        Optional weaknesses to apply to the damage, in the format
        ``{damage type: value}``, where the damage type may or may not match
        :attr:`Damage.type <pathfinder2e_stats.Damage.type>`; e.g. ``{"fire": 5}``.

        You may alternatively pass a :class:`~xarray.DataArray` with int dtype,
        a ``damage_type`` dimension with associated coordinate, and optional
        dimensions matching different targets.

        e.g.:

        >>> weaknesses = xarray.DataArray(
        ...     [[5, 5, 0], [0, 10, 10]], dims=["target", "damage_type"],
        ...     coords={"target": ["assassin vine", "zombie  brute"],
        ...             "damage_type": ["fire", "slashing", "vitality"]})

    :param resistances:
        Optional resistances to apply to the damage, in the same format as `weaknesses`.
    :param immunities:
        Optional immunities to apply to the damage, in the format
        ``[damage type, ...]`` or ``{damage type: bool}``; e.g.
        ``["fire"]`` or ``{"fire": True}``.

        .. note::

           Living creatures are not immune to vitality by default.
           If you want to simulate e.g. a :func:`~armory.runes.vitalizing`
           weapon against a living target, you must explicitly set
           ``immunities={"vitality": True}``.

        You may alternatively pass a :class:`~xarray.DataArray` with bool dtype and
        otherwise the same format as `weaknesses`.
        Continuing from the example above:

        >>> immunities = xarray.DataArray(
        ...     [[True, False], [False, True]],
        ...     dims=["target", "damage_type"],
        ...     coords={"target": ["assassin vine", "zombie  brute"],
        ...             "damage_type": ["vitality", "void"]})

    :param int persistent_damage_rounds:
        The number of rounds for which persistent
        damage should be applied at most, beyond which one expects that either the
        target was defeated or the encounter ended (and the persistent damage alone is
        assumed not to be life threatening). Default: 3 rounds.
    :param persistent_damage_DC:
        The DC of the flat check to end persistent damage.
        This may be an integer between 2 and 20, a dict mapping damage types to DCs,
        or a :class:`~xarray.DataArray` with the same format as `weaknesses`.
        Default: DC15.
    :param int splash_damage_targets:
        The number of targets affected by splash damage,
        including the main target. When calculating total damage, splash damage will be
        multiplied by this number. Default: 2 targets (main + 1 secondary target).
    :returns:
        A shallow copy of `check_outcome` with additional variables for the damage:

        damage_type
            Coordinate matching each damage type.
            Always one-dimensional even when there is a single damage type.
        direct_damage
            The direct damage dealt to the target, grouped by damage type.
            Has dimensions ``("roll", "damage_type")`` plus whatever additional
            dimensions ``check.outcome`` has.
            For each point it contains a roll of the `damage_spec` matching the
            check outcome, so in case of critical hit it is typically doubled
            (unless the damage spec specifies otherwise) etc.
            There is only one roll per outcome per `roll`, so e.g. in case of
            multiple targets the damage is rolled only once.
            Only present if there is any direct damage in the `damage_spec`.
        splash_damage
            The splash damage dealt to each target, with the same dimensions as
            `direct_damage`.
            Only present if there is any splash damage in the `damage_spec`.
        persistent_damage
            The persistent damage dealt, grouped by damage type, with dimensions
            ``("roll", "damage_type", "persistent_round")``.
            `persistent_round` has size equal to `persistent_damage_rounds` and no
            associated coordinate. Element 0 is the damage received at the end of
            the target's first round after the damage is applied, and so on.
            This is rolled before the flat check to end damage so it is always
            populated even after a successful check.
            Only present if there is any persistent damage in the `damage_spec`.
        persistent_damage_DC
            As the parameter.
            Only present if there is any persistent damage in the `damage_spec`.
        persistent_damage_check
            Outcome of the flat check to end persistent damage at the end of each
            round, with dimensions ``("roll", "damage_type", "persistent_round")``.
            Only present if there is any persistent damage in the `damage_spec`.
        apply_persistent_damage
            True if persistent damage is applied at the end of the target's
            round; False if there was a successful check on a previous round.
        total_damage
            An approximation of total damage dealt to the target(s), assuming that

            - there are `splash_damage_targets` targets affected by splash damage;
            - the target doesn't expire before the end of the persistent damage rounds;
            - there is no assistance to end persistent damage earlier.

            Total damage is calculated as::

                total_damage = (
                    direct_damage
                    + splash_damage * splash_damage_targets
                    + where(apply_persistent_damage, persistent_damage, 0)
                            .sum("persistent_round")
                ).sum("damage_type")

        The dataset also includes a new attribute:

        damage_spec
            String representation of the `damage_spec` parameter.

    **Examples:**

    Strike an AC17 enemy with a Longsword (+8 to hit, 1d8+4 damage):

    >>> spec = Damage("slashing", 1, 8, 4)
    >>> attack_roll = check(8, DC=17)
    >>> damage(attack_roll, spec)
    <xarray.Dataset> Size: 3MB
    Dimensions:        (roll: 100000, damage_type: 1)
    Coordinates:
      * damage_type    (damage_type) <U8 32B 'slashing'
    Dimensions without coordinates: roll
    Data variables:
        bonus          int64 8B 8
        DC             int64 8B 17
        natural        (roll) int64 800kB 18 13 11 6 7 1 2 1 ... 4 15 3 14 13 1 1 4
        outcome        (roll) int64 800kB 1 1 1 0 0 -1 0 -1 0 ... 0 1 0 1 1 -1 -1 0
        direct_damage  (roll, damage_type) int64 800kB 8 9 5 0 0 0 ... 0 11 6 0 0 0
        total_damage   (roll) int64 800kB 8 9 5 0 0 0 0 0 0 ... 0 0 5 0 11 6 0 0 0
    Attributes:
        legend:       {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'S...
        damage_spec:  {'Critical success': '(1d8+4)x2 slashing', 'Success': '1d8+...

    Strike with an :prd_equipment:`Alchemist's Fire <3287>`:

    >>> spec = (Damage("fire", 1, 8)
    ... + Damage("fire", 0, 0, 1, persistent=True)
    ... + Damage("fire", 0, 0, 1, splash=True))
    >>> attack_roll = check(8, DC=17)
    >>> damage(attack_roll, spec)
    <xarray.Dataset> Size: 9MB
    Dimensions:                  (roll: 100000, damage_type: 1, persistent_round: 3)
    Coordinates:
      * damage_type              (damage_type) <U4 16B 'fire'
    Dimensions without coordinates: roll, persistent_round
    Data variables:
        bonus                    int64 8B 8
        DC                       int64 8B 17
        natural                  (roll) int64 800kB 5 13 13 5 20 ... 10 9 11 12 12
        outcome                  (roll) int64 800kB 0 1 1 0 2 1 1 ... 0 0 1 1 1 1 1
        direct_damage            (roll, damage_type) int64 800kB 1 3 4 1 ... 3 7 6 5
        splash_damage            (roll, damage_type) int64 800kB 0 1 1 0 ... 1 1 1 1
        persistent_damage        (roll, damage_type, persistent_round) int64 2MB ...
        persistent_damage_DC     (damage_type) int64 8B 15
        persistent_damage_check  (roll, damage_type, persistent_round) int64 2MB ...
        apply_persistent_damage  (roll, damage_type, persistent_round) bool 300kB ...
        total_damage             (roll) int64 800kB 1 7 6 1 18 11 ... 1 6 7 11 9 9
    Attributes:
        legend:                 {-2: 'No roll', -1: 'Critical failure', 0: 'Failu...
        damage_spec:            {'Critical success': '(1d8)x2 fire plus 2 persist...
        splash_damage_targets:  2

    Engulf three targets in a :prd_spells:`Fireball <1530>` with DC21 basic reflex save.
    The targets have respectively Reflex bonus +11, +13, and +15.
    The last target also has resistance 5 to fire:

    >>> spec = Damage("fire", 6, 6, basic_save=True)
    >>> reflex_bonus = DataArray([11, 13, 15], dims=["target"])
    >>> resistances = DataArray(
    ...     [[0, 0, 5]], dims=["damage_type", "target"],
    ...     coords={"damage_type": ["fire"]})
    >>> # Roll savint throw separately for each target
    >>> saving_throw = check(reflex_bonus, DC=21, independent_dims=["target"])
    >>> dmg = damage(saving_throw, spec, resistances=resistances,
    ...              # Roll damage once for all targets and halve/double as needed
    ...              dependent_dims=["target"])
    >>> dmg
    <xarray.Dataset> Size: 10MB
    Dimensions:        (target: 3, roll: 100000, damage_type: 1)
    Coordinates:
      * damage_type    (damage_type) <U4 16B 'fire'
    Dimensions without coordinates: target, roll
    Data variables:
        bonus          (target) int64 24B 11 13 15
        DC             int64 8B 21
        natural        (roll, target) int64 2MB 13 4 9 11 12 7 5 ... 12 2 3 7 11 4 1
        outcome        (roll, target) int64 2MB 1 0 1 1 1 1 0 1 ... 0 1 0 0 1 1 0 -1
        direct_damage  (roll, target, damage_type) int64 2MB 15 30 10 11 ... 6 13 21
        resistances    (damage_type, target) int64 24B 0 0 5
        total_damage   (roll, target) int64 2MB 15 30 10 11 11 6 ... 12 12 1 6 13 21
    Attributes:
        legend:       {-2: 'No roll', -1: 'Critical failure', 0: 'Failure', 1: 'S...
        damage_spec:  {'Success': '(6d6)/2 fire', 'Failure': '6d6 fire', 'Critica...

    How much damage did each target take, on average?

    >>> dmg.total_damage.mean("roll").to_pandas()
    target
    0    15.65510
    1    13.47350
    2     7.64498
    Name: total_damage, dtype: float64
    """
    out = check_outcome.copy(deep=False)
    damage_spec = ExpandedDamage(damage_spec)
    out.attrs["damage_spec"] = damage_spec.to_dict_of_str()

    independent_dims = _parse_independent_dependent_dims(
        "damage", check_outcome, independent_dims, dependent_dims
    )

    # For persistent damage, treat all dimensions as independent.
    # Note: this is not *quite* right. Consider:
    # Swipe: attack roll is dependent on target, damage is dependent too,
    #        but check to recover from persistent damage is independent.
    # What-if analysis of persistent damage vs. different targets:
    #        persistent damage is dependent too.
    # This last case is not modelled exactly for the sake of not
    # overwhelming the user with configuration options.
    persistent_independent_dims = dict(check_outcome.sizes)
    del persistent_independent_dims["roll"]
    persistent_independent_dims["persistent_round"] = persistent_damage_rounds

    damages = {
        name: _roll_damage(check_outcome.outcome, spec, dims)
        for name, spec, dims in (
            ("direct_damage", damage_spec.filter("direct"), independent_dims),
            ("splash_damage", damage_spec.filter("splash"), independent_dims),
            (
                "persistent_damage",
                damage_spec.filter("persistent"),
                persistent_independent_dims,
            ),
        )
        if spec
    }
    damages = dict(
        zip(
            damages,
            xarray.align(*damages.values(), join="outer", copy=False, fill_value=0),
            strict=False,
        )
    )
    out.update(damages)

    if "splash_damage" in out:
        if "direct_damage" in out:
            out["direct_damage"] += out["splash_damage"]
        else:
            out["direct_damage"] = out["splash_damage"]

    weaknesses = _parse_weaknesses(weaknesses)
    resistances = _parse_weaknesses(resistances)
    immunities = _parse_weaknesses(immunities)
    _, weaknesses, resistances, immunities = xarray.align(
        out, weaknesses, resistances, immunities, join="left", copy=False, fill_value=0
    )
    immunities = immunities.astype(bool)
    if weaknesses.any():
        out["weaknesses"] = weaknesses
    if resistances.any():
        out["resistances"] = resistances
    if immunities.any():
        out["immunities"] = immunities

    for k in ("direct_damage", "splash_damage", "persistent_damage"):
        if k in out:
            damage = out[k]
            damage = damage.where(~immunities, 0)
            damage = cast(DataArray, np.maximum(0, damage - resistances))
            damage = damage + xarray.where(damage > 0, weaknesses, 0)
            out[k] = damage

    total_damage = []
    if "direct_damage" in out:
        total_damage.append(out["direct_damage"])
    if "splash_damage" in out:
        out.attrs["splash_damage_targets"] = splash_damage_targets
        # Splash damage to main target is already included in direct damage
        total_damage.append(out["splash_damage"] * (splash_damage_targets - 1))
    if "persistent_damage" in out:
        if isinstance(persistent_damage_DC, int):
            persistent_damage_DC = dict.fromkeys(
                out.damage_type.values, persistent_damage_DC
            )
        persistent_damage_DC = _parse_weaknesses(persistent_damage_DC)
        _, persistent_damage_DC = xarray.align(
            out, persistent_damage_DC, join="left", fill_value=15
        )
        out["persistent_damage_DC"] = persistent_damage_DC

        out["persistent_damage_check"] = check(
            DC=persistent_damage_DC,
            # Roll separately for each damage type, but not e.g. for different targets
            independent_dims={
                # For persistent damage, treat all dimensions as independent.
                # Read note above.
                "damage_type": out.sizes["damage_type"],
                **persistent_independent_dims,
                **dict.fromkeys(out["persistent_damage_DC"].dims),
            },
            allow_critical_failure=False,
            allow_critical_success=False,
        ).outcome
        out["apply_persistent_damage"] = (
            out["persistent_damage_check"]
            .cumsum("persistent_round")
            # Check to extinguish persistent damage is done after taking it
            .shift({"persistent_round": 1}, fill_value=0)
            == 0
        )
        total_damage.append(
            (out["persistent_damage"] * out["apply_persistent_damage"]).sum(
                "persistent_round"
            )
        )

    if total_damage:
        out["total_damage"] = sum(total_damage).sum("damage_type")  # type: ignore[union-attr]
        out["damage_type"] = out["damage_type"].astype("U")
    else:
        out["total_damage"] = xarray.zeros_like(out["outcome"])
        out["damage_type"] = ("damage_type", np.asarray([], dtype="U"))

    return out


def _roll_damage(
    check_outcome: DataArray,
    spec: ExpandedDamage,
    independent_dims: Mapping[Hashable, int],
) -> DataArray:
    # Only roll once and then double/halve instead of rolling separately for each
    # outcome. This matters in case of multiple targets receiving the same damage.
    cache: dict[Damage, xarray.DataArray] = {}

    dmg_by_dos = []  # dims=(roll, damage_type)
    for specs in spec.values():
        dmg_by_type = []  # dims=(roll,); specific for the current DoS
        for d in specs:
            # Cache key includes in the damage type, persistent, and splash
            # Don't include multiplier in the cache key, so that along all
            # dependent dimensions you roll damage only once and then
            # double/halve it as needed.
            key = d.copy(multiplier=1)
            try:
                r = cache[key]
            except KeyError:
                r = roll(d.dice, d.faces, d.bonus, dims=independent_dims)
                cache[key] = r

            assert d.multiplier in (0.5, 1, 2)
            if d.multiplier == 2:
                r = r * 2  # Don't use *= to avoid modifying the cache
            elif d.multiplier == 0.5:
                r = r // 2

            # Halved damage is rounded down, but can't be reduced below 1.
            # If the combined penalties on an attack would reduce the damage to 0 or
            # below, you still deal 1 damage.
            r = cast(DataArray, np.maximum(1, r))

            dmg_by_type.append(r)

        r = xarray.concat(dmg_by_type, dim="damage_type", join="outer", fill_value=0)
        r.coords["damage_type"] = [d.type for d in specs]
        r = r.groupby("damage_type", squeeze=False).sum()
        dmg_by_dos.append(r)

    dmg_by_dos = list(xarray.align(*dmg_by_dos, copy=False, join="outer", fill_value=0))
    return sum(
        xarray.where(check_outcome == dos, dmg, 0)
        for dos, dmg in zip(spec, dmg_by_dos, strict=False)
    )


def _parse_weaknesses(a: Collection[str] | DataArray | None) -> DataArray:
    if isinstance(a, DataArray):
        pass
    elif not a:
        a = DataArray([], dims=["damage_type"], coords={"damage_type": []}).astype(int)
    else:
        if not isinstance(a, Mapping):
            a = dict.fromkeys(a, True)  # immunities
        a = DataArray(
            list(a.values()),
            dims=["damage_type"],
            coords={"damage_type": list(a)},
        )

    if "damage_type" not in a.dims or (
        a.sizes["damage_type"] and "damage_type" not in a.coords
    ):
        raise ValueError(
            f"Expected DataArray with labelled dimension 'damage_type'; got {a}"
        )
    if a.dtype != bool and a.dtype.kind != "i":
        raise ValueError(f"Expected DataArray with int or bool dtype; got {a}")
    return a
