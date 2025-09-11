from __future__ import annotations

import numpy as np
import pytest
import xarray
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import Damage, DoS, check, damage, set_config


def test_damage_simple():
    actual = damage(check(16, DC=21), Damage("slashing", 1, 6, 3, deadly=8))
    assert np.unique(actual.outcome).tolist() == [-1, 0, 1, 2]

    assert actual.direct_damage.sizes == {"roll": 1000, "damage_type": 1}
    assert actual.total_damage.sizes == {"roll": 1000}
    assert actual.damage_type.values.tolist() == ["slashing"]
    assert actual.direct_damage[actual.outcome == -1].sum() == 0
    assert actual.direct_damage[actual.outcome == 0].sum() == 0
    assert actual.direct_damage[actual.outcome == 1].min() == 1 + 3
    assert actual.direct_damage[actual.outcome == 1].max() == 6 + 3
    assert actual.direct_damage[actual.outcome == 2].min() == (1 + 3) * 2 + 1
    assert actual.direct_damage[actual.outcome == 2].max() == (6 + 3) * 2 + 8

    assert_equal(actual.direct_damage.sum("damage_type"), actual.total_damage)
    assert "splash_damage" not in actual
    assert "persistent_damage" not in actual
    assert "weaknesses" not in actual
    assert "resistances" not in actual
    assert "immunities" not in actual

    assert actual.attrs["damage_spec"] == {
        "Success": "1d6+3 slashing",
        "Critical success": "(1d6+3)x2 slashing plus 1d8 slashing",
    }


def test_no_damage():
    """We can only assume that a damage of 0d0+0 was meant to have a positive
    bonus which was then negated by a penalty.

    However, if the combined penalties on an attack would reduce the damage to
    0 or below, you still deal 1 damage.
    """
    actual = damage(check(16, DC=21), Damage("slashing", 0, 0, 0))
    assert actual.total_damage.sizes == {"roll": 1000}
    assert actual.total_damage.max() == 1
    assert "direct_damage" in actual


def test_splash_damage():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 8) + Damage("fire", 0, 0, 1, splash=True),
        splash_damage_targets=4,
    )
    assert actual.total_damage[actual.outcome == -1].max() == 0

    # Secondary targets don't get splash damage on a failure
    assert actual.direct_damage[actual.outcome == 0].min() == 1
    assert actual.direct_damage[actual.outcome == 0].max() == 1
    assert actual.splash_damage[actual.outcome == 0].max() == 0
    assert actual.total_damage[actual.outcome == 0].min() == 1
    assert actual.total_damage[actual.outcome == 0].max() == 1

    # Main target splash has been added to direct damage
    assert actual.direct_damage[actual.outcome == 1].min() == 1 + 1
    assert actual.direct_damage[actual.outcome == 1].max() == 8 + 1
    assert actual.splash_damage[actual.outcome == 1].min() == 1
    assert actual.splash_damage[actual.outcome == 1].max() == 1
    assert actual.total_damage[actual.outcome == 1].min() == 1 + 4
    assert actual.total_damage[actual.outcome == 1].max() == 8 + 4

    # Splash damage is not doubled on a critical hit
    assert actual.direct_damage[actual.outcome == 2].min() == 1 * 2 + 1
    assert actual.direct_damage[actual.outcome == 2].max() == 8 * 2 + 1
    assert actual.splash_damage[actual.outcome == 2].min() == 1
    assert actual.splash_damage[actual.outcome == 2].max() == 1
    assert actual.total_damage[actual.outcome == 2].min() == 1 * 2 + 4
    assert actual.total_damage[actual.outcome == 2].max() == 8 * 2 + 4


def test_splash_damage_no_direct():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 0, 0, 1, splash=True),
        splash_damage_targets=4,
    )
    assert actual.total_damage[actual.outcome == -1].max() == 0

    # Main target splash has been added to direct damage, even if
    # there's no direct damage anyway.
    # Secondary targets don't get splash damage on a failure.
    assert actual.direct_damage[actual.outcome == 0].min() == 1
    assert actual.direct_damage[actual.outcome == 0].max() == 1
    assert actual.splash_damage[actual.outcome == 0].max() == 0
    assert actual.total_damage[actual.outcome == 0].min() == 1
    assert actual.total_damage[actual.outcome == 0].max() == 1
    for o in (1, 2):
        assert actual.direct_damage[actual.outcome == o].min() == 1
        assert actual.direct_damage[actual.outcome == o].max() == 1
        assert actual.splash_damage[actual.outcome == o].min() == 1
        assert actual.splash_damage[actual.outcome == o].max() == 1
        assert actual.total_damage[actual.outcome == o].min() == 4
        assert actual.total_damage[actual.outcome == o].max() == 4


def test_persistent_damage():
    actual = damage(check(6, DC=15), Damage("fire", 1, 6, persistent=True))
    assert "direct_damage" not in actual
    assert "splash_damage" not in actual
    assert actual.persistent_damage.sizes == {
        "roll": 1000,
        "damage_type": 1,
        "persistent_round": 3,
    }
    assert actual.total_damage.sizes == {"roll": 1000}

    assert actual.persistent_damage[actual.outcome > 0].min() == 1
    assert actual.persistent_damage.max() == 12
    assert actual.persistent_damage_check.min() == 0
    assert actual.persistent_damage_check.max() == 1
    assert actual.apply_persistent_damage.isel(persistent_round=0).all()
    assert 0.65 < actual.apply_persistent_damage.isel(persistent_round=1).mean() < 0.75
    assert 0.44 < actual.apply_persistent_damage.isel(persistent_round=2).mean() < 0.54

    assert actual.total_damage[actual.outcome <= 0].sum() == 0
    assert actual.total_damage[actual.outcome == 1].min() == 1
    assert actual.total_damage[actual.outcome == 2].min() == 2
    assert 16 < actual.total_damage[actual.outcome == 1].max() <= 18
    assert 30 < actual.total_damage[actual.outcome == 2].max() <= 36


def test_persistent_damage_DC20():
    actual = damage(
        check(6, DC=15),
        Damage("bleed", 0, 0, 1, persistent=True),
        persistent_damage_DC=20,
    )
    assert actual.persistent_damage_check.min() == 0
    assert actual.persistent_damage_check.max() == 1
    assert 0.03 < actual.persistent_damage_check.mean() < 0.07
    assert actual.apply_persistent_damage.isel(persistent_round=0).all()
    assert 0.93 < actual.apply_persistent_damage.isel(persistent_round=1).mean() < 0.97
    assert 0.88 < actual.apply_persistent_damage.isel(persistent_round=2).mean() < 0.92
    assert 2.7 < actual.total_damage[actual.outcome == 1].mean() < 2.9


def test_persistent_damage_DC10():
    actual = damage(
        check(6, DC=15),
        Damage("bleed", 0, 0, 1, persistent=True),
        persistent_damage_DC=10,
    )
    assert actual.persistent_damage_check.min() == 0
    assert actual.persistent_damage_check.max() == 1
    assert 0.52 < actual.persistent_damage_check.mean() < 0.57
    assert actual.apply_persistent_damage.isel(persistent_round=0).all()
    assert 0.42 < actual.apply_persistent_damage.isel(persistent_round=1).mean() < 0.47
    assert 0.18 < actual.apply_persistent_damage.isel(persistent_round=2).mean() < 0.22
    assert 1.5 < actual.total_damage[actual.outcome == 1].mean() < 1.9


def test_multiple_persistent_damages():
    """Persistent damages of different types roll to stop separately"""
    actual = damage(
        check(6, DC=15),
        Damage("bleed", 0, 0, 1, persistent=True)
        + Damage("fire", 0, 0, 1, persistent=True),
    )
    assert actual.apply_persistent_damage.sizes == {
        "roll": 1000,
        "damage_type": 2,
        "persistent_round": 3,
    }
    bleed = actual.apply_persistent_damage.sel(damage_type="bleed", drop=True)
    fire = actual.apply_persistent_damage.sel(damage_type="fire", drop=True)
    assert not (bleed == fire).all()


@pytest.mark.parametrize(
    "DC",
    [
        {"bleed": 20, "fire": 10, "electricity": 12},
        DataArray(
            [20, 10, 12],
            dims=["damage_type"],
            coords={"damage_type": ["bleed", "fire", "electricity"]},
        ),
    ],
)
def test_multiple_persistent_damage_DCs(DC):
    """Different persistent damage types can have different DCs"""
    actual = damage(
        check(6, DC=15),
        Damage("bleed", 0, 0, 1, persistent=True)
        + Damage("fire", 0, 0, 1, persistent=True)
        + Damage("cold", 0, 0, 1, persistent=True),
        persistent_damage_DC=DC,
    )
    # Omitted goes to default
    assert_equal(
        actual.persistent_damage_DC,
        DataArray(
            [20, 15, 10],
            dims=["damage_type"],
            coords={"damage_type": ["bleed", "cold", "fire"]},
        ),
    )

    assert actual.apply_persistent_damage.sizes == {
        "roll": 1000,
        "damage_type": 3,
        "persistent_round": 3,
    }
    means = (
        actual.apply_persistent_damage.mean("roll")
        .sum("persistent_round")
        .values.tolist()
    )
    assert 2.7 < means[0] < 2.9  # bleed
    assert 2.0 < means[1] < 2.4  # cold
    assert 1.5 < means[2] < 1.8  # fire


def test_minimum_damage():
    """If a penalty to damage would reduce it to 0, it still deals 1"""
    actual = damage(check(6, DC=15), Damage("slashing", 1, 6, -2))
    assert actual.total_damage[actual.outcome == 1].max() == 4
    assert actual.total_damage[actual.outcome == 1].min() == 1


@pytest.mark.parametrize(
    "immunities",
    [
        ["fire"],
        ("fire", "cold"),
        {"fire": True},
        {"fire": True, "cold": True, "slashing": False},
        DataArray(
            [True, True],
            dims=["damage_type"],
            coords={"damage_type": ["cold", "fire"]},
        ),
    ],
)
def test_immunities(immunities):
    actual = damage(
        check(6, DC=15),
        Damage("slashing", 1, 6) + Damage("fire", 0, 0, 1),
        immunities=immunities,
    )
    assert actual.immunities.dtype == bool
    expect = DataArray(
        [False, True],
        dims=["damage_type"],
        coords={"damage_type": ["slashing", "fire"]},
    )
    # Different versions of xarray produce different orderings
    actual, expect = xarray.align(actual, expect, join="outer")
    assert_equal(actual.immunities, expect)
    assert actual.direct_damage.sel(damage_type="slashing").max() == 12
    assert actual.direct_damage.sel(damage_type="fire").max() == 0


def test_weaknesses():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 6, basic_save=True),
        weaknesses={"fire": 10},
    )
    # Weaknesses don't double on a crit fail
    assert actual.total_damage[actual.outcome == -1].max() == 22
    # Weaknesses don't halve on a success
    assert actual.total_damage[actual.outcome == 1].max() == 13


def test_resistances():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 6, basic_save=True),
        resistances={"fire": 5},
    )
    assert np.unique(actual.total_damage[actual.outcome == 0]).tolist() == [0, 1]
    # Resistances don't double on a crit fail
    assert actual.total_damage[actual.outcome == -1].max() == 7
    # Resistances don't halve on a success
    assert actual.total_damage[actual.outcome == 1].max() == 0


def test_weaknesses_splash():
    """Splash damage adds to direct before calculating weaknesses"""
    actual = damage(
        check(6, DC=15),
        Damage("fire", 0, 0, 1) + Damage("fire", 0, 0, 1, splash=True),
        weaknesses={"fire": 10},
        splash_damage_targets=3,
    )
    assert (actual.total_damage[actual.outcome == 1] == 34).all()


def test_resistances_splash():
    """Splash damage adds to direct before calculating resistances"""
    actual = damage(
        check(6, DC=15),
        Damage("fire", 0, 0, 4) + Damage("fire", 0, 0, 3, splash=True),
        resistances={"fire": 5},
        splash_damage_targets=9,
    )
    # 2 damage to main target, 0 to others
    assert (actual.total_damage[actual.outcome == 1] == 2).all()


def test_weaknesses_persistent():
    """Weaknesses re-apply at every application of persistent damage"""
    actual = damage(
        check(6, DC=15),
        Damage("fire", 0, 0, 1) + Damage("fire", 0, 0, 1, persistent=True),
        weaknesses={"fire": 10},
    )
    assert actual.total_damage[actual.outcome == 1].min() == 22  # at least 1 round
    assert actual.total_damage[actual.outcome == 2].min() == 24
    assert actual.total_damage[actual.outcome == 1].max() == 44  # 2 failed saves
    assert actual.total_damage[actual.outcome == 2].max() == 48


def test_resistances_persistent():
    """Resistances re-apply at every application of persistent damage"""
    set_config(roll_size=10_000)

    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 6) + Damage("fire", 1, 6, persistent=True),
        resistances={"fire": 5},
    )
    assert actual.direct_damage[actual.outcome == 1].max() == 1
    assert_equal(
        actual.persistent_damage[actual.outcome == 1].max(["roll", "damage_type"]),
        DataArray([1, 1, 1], dims=["persistent_round"]),
    )
    assert actual.total_damage[actual.outcome > 0].min() == 0
    assert actual.total_damage[actual.outcome == 1].max() == 4  # 2 failed saves
    assert 25 < actual.total_damage[actual.outcome == 2].max() <= 28


def test_apply_weakness_once():
    """Multiple sources of immediate damage off the same type trigger weaknesses and
    resistances only once
    """
    actual = damage(
        check(6, DC=15),
        Damage("slashing", 1, 6, deadly=8),
        weaknesses={"slashing": 10},
    )
    assert actual.total_damage[actual.outcome == 2].min() == 1 * 2 + 1 + 10
    assert actual.total_damage.max() == 6 * 2 + 8 + 10


def test_apply_resistance_once():
    """Multiple sources of immediate damage off the same type trigger weaknesses and
    resistances only once
    """
    actual = damage(
        check(6, DC=15),
        Damage("slashing", 1, 6, deadly=8),
        resistances={"slashing": 10},
    )
    assert actual.total_damage[actual.outcome == 2].min() == 0
    assert actual.total_damage.max() == 6 * 2 + 8 - 10


@pytest.mark.parametrize("key", ["weaknesses", "resistances", "immunities"])
def test_weaknesses_array(key):
    actual = damage(
        check(6, DC=15),
        Damage("slashing", 1, 6, deadly=8),
        **{
            key: DataArray(
                [[1, 0], [0, 1]],
                dims=["damage_type", "target"],
                coords={"damage_type": ["fire", "slashing"], "target": ["foo", "bar"]},
            )
        },
    )
    assert actual.total_damage.sizes == {"roll": 1000, "target": 2}
    assert actual.target.values.tolist() == ["foo", "bar"]


@pytest.mark.parametrize("key", ["weaknesses", "resistances", "immunities"])
def test_malformed_weaknesses(key):
    with pytest.raises(ValueError, match="Expected DataArray with int or bool dtype"):
        damage(
            check(6, DC=15),
            Damage("slashing", 1, 6),
            **{key: {"fire": 0.5}},
        )

    with pytest.raises(ValueError, match="Expected DataArray with labelled dimension"):
        damage(
            check(6, DC=15),
            Damage("slashing", 1, 6),
            **{key: DataArray(1)},
        )


def test_basic_save():
    """Halving the damage on a basic save rounds down to integer"""
    actual = damage(check(6, DC=15), Damage("fire", 1, 6, basic_save=True))
    assert actual.direct_damage.dtype.kind == "i"
    assert actual.total_damage.dtype.kind == "i"
    assert actual.total_damage[actual.outcome == -1].max() == 12
    assert actual.total_damage[actual.outcome == 0].max() == 6

    # Halving damage can't reduce damage below 1
    assert np.unique(actual.total_damage[actual.outcome == 1]).tolist() == [1, 2, 3]
    assert actual.total_damage[actual.outcome == 2].max() == 0


def test_basic_save_fixed():
    # Rounded down
    actual = damage(check(6, DC=15), Damage("fire", 0, 0, 5, basic_save=True))
    assert np.unique(actual.total_damage[actual.outcome == 1]).tolist() == [2]

    # Halving damage can't reduce damage below 1
    actual = damage(check(6, DC=15), Damage("fire", 0, 0, 1, basic_save=True))
    assert np.unique(actual.total_damage[actual.outcome == 1]).tolist() == [1]


def test_multiple_targets():
    """In case of multiple targets along a dependent_dim, damage is rolled only once
    and then multiplied/halved.
    """
    set_config(roll_size=50)
    actual = damage(
        check(6, DC=15, independent_dims={"target": 1000}),
        Damage("fire", 6, 6, basic_save=True),
        dependent_dims=["target"],
    )
    d = actual.total_damage.values
    assert d.shape == (50, 1000)
    assert np.unique(d).size > 10
    for i in range(d.shape[0]):
        u = np.unique(d[i])
        assert u.size == 4, u  # Different targets get the same damage for each outcome
        assert u[0] == 0, u  # Critical success
        assert u[1] == u[2] // 2, u  # Success halves damage
        assert u[3] == u[2] * 2, u  # Critical failure doubles damage


def test_multiple_targets_splash():
    """In case of multiple targets along a dependent_dim, damage is rolled only once.
    This includes when there is no multiplier.
    """
    set_config(roll_size=50)
    actual = damage(
        check(6, DC=15, independent_dims={"target": 1000}),
        Damage("fire", 6, 6, splash=True),
        dependent_dims=["target"],
    ).total_damage.values
    assert actual.shape == (50, 1000)
    assert np.unique(actual).size > 10
    for i in range(actual.shape[0]):
        u = np.unique(actual[i])
        # Different targets get the same damage for each outcome, except on a miss,
        # where only the primary target takes damage
        assert u.size == 3, u
        assert u[0] == 0, u  # Critical failure
        assert u[1] > 0, u  # Failure, success, critical success


def test_multiple_targets_deadly():
    """If you hit multiple targets with a deadly weapon, but you only roll damage once
    (e.g. Swipe), then roll the base damage only once for all, then double it, then roll
    the deadly die.
    """
    set_config(roll_size=50)
    actual = damage(
        check(6, DC=15, independent_dims={"target": 1000}),
        Damage("slashing", 2, 12, deadly=6),
        dependent_dims=["target"],
    ).total_damage.values
    assert actual.shape == (50, 1000)  # {roll: 50, target: 1000}
    assert np.unique(actual).size > 10
    for i in range(actual.shape[0]):
        u = np.unique(actual[i])
        assert u.size == 3, u  # Different targets get the same damage for each outcome
        assert u[0] == 0, u  # Critical failure
        assert u[2] >= u[1] * 2 + 1
        assert u[2] <= u[1] * 2 + 6


def test_multiple_targets_type():
    """In case of multiple targets of e.g. a fireball, damage is rolled only once
    for half, full, and double.
    However, identical damage dice with different types are rolled separately.
    You do not need to explicitly state that 'damage_type' is an dependent dimension.

    # TODO weaknesses with damage_type dim
    """
    set_config(roll_size=50)
    actual = damage(
        check(6, DC=15, independent_dims={"target": 1000}),
        Damage("fire", 50, 12) + Damage("cold", 50, 12),
        dependent_dims=["target"],
    )
    d = actual.direct_damage.values
    assert d.shape == (50, 1000, 2)  # {roll: 50, target: 1000, damage_type: 2}
    assert np.unique(d).size > 10
    for i in range(d.shape[0]):
        u_fire = np.unique(d[i, :, 0])
        u_cold = np.unique(d[i, :, 1])
        assert u_fire.size == 3  # [crit fail | fail, success, crit success]
        assert u_cold.size == 3
        assert u_fire[0] == 0
        assert u_fire[1] > 0
        assert u_fire[2] == u_fire[1] * 2
        assert u_cold[0] == 0
        assert u_cold[1] > 0
        assert u_cold[2] == u_cold[1] * 2
        assert u_fire[1] != u_cold[1], (u_fire, u_cold)


def test_multiple_targets_type_splash():
    """Same as test_multiple_targets_type, but for splash damage"""
    set_config(roll_size=50)
    actual = damage(
        check(6, DC=15, independent_dims={"target": 1000}),
        Damage("fire", 50, 12, splash=True) + Damage("cold", 50, 12, splash=True),
        dependent_dims=["target"],
    )
    d = actual.splash_damage.values
    assert d.shape == (50, 1000, 2)  # {roll: 50, target: 1000, damage_type: 2}
    assert np.unique(d).size > 10
    for i in range(d.shape[0]):
        u_fire = np.unique(d[i, :, 0])
        u_cold = np.unique(d[i, :, 1])
        assert u_fire.size == 2  # [crit fail | fail, success | crit success]
        assert u_cold.size == 2
        assert u_fire[0] == 0
        assert u_fire[1] > 0
        assert u_cold[0] == 0
        assert u_cold[1] > 0
        assert u_fire[1] != u_cold[1], (u_fire, u_cold)


def test_independent_dims():
    """Test damage() parameters independent_dims and dependent_dims.

    See also
    --------
    test_check.py::test_independent_dims()
    test_tools.py::test_parse_independent_dependent_dims()
    """
    c = check(6, DC=15, independent_dims={"target": 2})
    s = Damage("fire", 6, 6, basic_save=True)

    ind = damage(c, s, independent_dims=["target"])
    dep = damage(c, s, dependent_dims=["target"])

    c0 = c.outcome.isel(target=0)
    c1 = c.outcome.isel(target=1)
    ind0 = ind.total_damage.isel(target=0)
    ind1 = ind.total_damage.isel(target=1)
    dep0 = dep.total_damage.isel(target=0)
    dep1 = dep.total_damage.isel(target=1)

    mask = c0 == c1
    assert mask.any()
    assert_equal(dep0[mask], dep1[mask])
    assert (ind0[mask] == ind1[mask]).any()
    assert (ind0[mask] != ind1[mask]).any()

    mask = c0 != c1
    assert mask.any()
    assert (dep0[mask] != dep1[mask]).all()
    assert (ind0[mask] == ind1[mask]).any()
    assert (ind0[mask] != ind1[mask]).any()

    # Roll once along dependent dims and then halve/double for
    # successful save or critical failure.
    mask = (c0 == DoS.failure) & (c1 == DoS.critical_failure)
    assert mask.any()
    assert_equal(dep1[mask], dep0[mask] * 2)

    mask = (c0 == DoS.failure) & (c1 == DoS.success)
    assert mask.any()
    assert_equal(dep1[mask], dep0[mask] // 2)


def test_damage_type_independent_dims():
    """Damage of different types is rolled separately"""
    c = check(6, DC=15)
    s = Damage("fire", 1, 6) + Damage("cold", 1, 6)
    d = damage(c, s)
    fire = d.direct_damage.sel(damage_type="fire", drop=True)
    cold = d.direct_damage.sel(damage_type="cold", drop=True)
    assert (fire != cold).any()


def test_splash_damage_is_independent():
    """direct and splash damages are rolled separately"""
    c = check(6, DC=15)
    s = Damage("fire", 1, 6) + Damage("fire", 1, 6, splash=True)
    d = damage(c, s, splash_damage_targets=1)
    assert (d.direct_damage != d.splash_damage).any()


def test_persistent_damage_independent_dims():
    """Persistent damage and recovery checks are always independent, regardless of
    initial damage.
    """
    c = check(6, DC=DataArray([15, 15], dims=["target"]), dependent_dims=["target"])
    s = Damage("fire", 1, 6, persistent=True) + Damage("cold", 1, 6, persistent=True)
    d = damage(c, s, dependent_dims=["target"])
    d = d.sel(roll=d.outcome.isel(target=0) == DoS.success)
    assert (d.outcome == DoS.success).all()  # target is a dependent dim

    for var in d.persistent_damage, d.persistent_damage_check:
        # test target dim is independent
        assert (
            var.isel(target=0, persistent_round=0, damage_type=0)
            != var.isel(target=1, persistent_round=0, damage_type=0)
        ).any()
        # test persistent_round dim is independent
        assert (
            var.isel(target=0, persistent_round=0, damage_type=0)
            != var.isel(target=0, persistent_round=1, damage_type=0)
        ).any()
        # test damage_type dim is independent
        # (this is not obvious for the recovery check!)
        assert (
            var.isel(target=0, persistent_round=0, damage_type=0)
            != var.isel(target=0, persistent_round=0, damage_type=1)
        ).any()


def test_null_damage():
    actual = damage(check(6, DC=15), {})
    assert actual.sizes == {"roll": 1000, "damage_type": 0}
    assert actual.damage_type.shape == (0,)
    assert actual.damage_type.dtype.kind == "U"
    assert actual.total_damage.shape == (1000,)
    assert actual.total_damage.dtype.kind == "i"
    assert (actual.total_damage == 0).all()
