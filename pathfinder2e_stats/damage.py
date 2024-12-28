from __future__ import annotations

from collections.abc import Collection, Hashable, Mapping
from typing import cast

import numpy as np
import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.check import check
from pathfinder2e_stats.damage_spec import AnyDamageSpec, ExpandedDamage
from pathfinder2e_stats.dice import roll


def damage(
    check_outcome: Dataset,
    damage_spec: AnyDamageSpec,
    *,
    weaknesses: Mapping[str, int] | DataArray | None = None,
    resistances: Mapping[str, int] | DataArray | None = None,
    immunities: Mapping[str, bool] | Collection[str] | DataArray | None = None,
    persistent_damage_rounds: int = 3,
    persistent_damage_DC: int | Mapping[str, int] | DataArray = 15,
    splash_damage_targets: int = 2,
) -> Dataset:
    out = check_outcome.copy(deep=False)
    damage_spec = ExpandedDamage(damage_spec)
    out.attrs["damage_spec"] = damage_spec.to_dict_of_str()

    damages = {
        name: _roll_damage(check_outcome.outcome, spec, dims)
        for name, spec, dims in (
            ("direct_damage", damage_spec.filter(), None),
            ("splash_damage", damage_spec.filter(splash=True), None),
            (
                "persistent_damage",
                damage_spec.filter(persistent=True),
                {"persistent_round": persistent_damage_rounds},
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
            persistent_damage_DC = {
                k: persistent_damage_DC for k in out.damage_type.values
            }
        persistent_damage_DC = _parse_weaknesses(persistent_damage_DC)
        _, persistent_damage_DC = xarray.align(
            out, persistent_damage_DC, join="left", fill_value=15
        )
        out["persistent_damage_DC"] = persistent_damage_DC

        out["persistent_damage_check"] = check(
            DC=persistent_damage_DC,
            # Roll separately for each damage type, but not e.g. for different targets
            dims={
                "damage_type": out.sizes["damage_type"],
                "persistent_round": persistent_damage_rounds,
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
    else:
        out["total_damage"] = xarray.zeros_like(out["outcome"])

    return out


def _roll_damage(
    check_outcome: DataArray, spec: ExpandedDamage, dims: dict[str, int] | None
) -> DataArray:
    out = []
    for specs in spec.values():
        damage_rolls = []
        for d in specs:
            r = roll(d.dice, d.faces, d.bonus, dims=cast(Mapping[Hashable, int], dims))

            if d.multiplier == 2:
                r *= 2
            elif d.multiplier == 0.5:
                r //= 2
            else:
                assert d.multiplier == 1

            damage_rolls.append(r)

        r = xarray.concat(damage_rolls, dim="damage_type", join="outer", fill_value=0)
        del damage_rolls
        r.coords["damage_type"] = [d.type for d in specs]
        r = r.groupby("damage_type", squeeze=False).sum()
        out.append(r)

    out = list(xarray.align(*out, copy=False, join="outer", fill_value=0))
    return sum(
        xarray.where(check_outcome == dos, r, 0)
        for dos, r in zip(spec, out, strict=False)
    )


def _parse_weaknesses(a: Collection[str] | DataArray | None) -> DataArray:
    if isinstance(a, DataArray):
        pass
    elif not a:
        a = DataArray([], dims=["damage_type"], coords={"damage_type": []}).astype(int)
    else:
        if not isinstance(a, Mapping):
            a = {k: True for k in a}  # immunities
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
