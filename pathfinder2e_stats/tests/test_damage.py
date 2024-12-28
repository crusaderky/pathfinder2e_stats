from __future__ import annotations

import numpy as np
import pytest
import xarray
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import Damage, check, damage, set_size


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
    actual = damage(check(16, DC=21), Damage("slashing", 0, 0, 0))
    assert actual.total_damage.sizes == {"roll": 1000}
    assert actual.total_damage.sum() == 0
    assert "initial_damage" not in actual
    assert "splash_damage" not in actual
    assert "persistent_damage" not in actual


@pytest.mark.parametrize("bonus", [0, 1])
def test_no_damage_consistent_shape(bonus):
    actual = damage(
        check(
            16,
            DC=DataArray([20, 22, 24], dims=["target"]),
            dims={"foo": 2},
        ),
        Damage("slashing", 0, 0, bonus),
    )
    assert actual.total_damage.sizes == {"roll": 1000, "target": 3, "foo": 2}
    assert actual.total_damage.min() == 0
    assert actual.total_damage.max() == bonus * 2


def test_splash_damage():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 8) + Damage("fire", 0, 0, 1, splash=True),
        splash_damage_targets=4,
    )
    assert actual.total_damage[actual.outcome == -1].sum() == 0
    assert actual.total_damage[actual.outcome == 0].min() == 4
    assert actual.total_damage[actual.outcome == 0].max() == 4

    # Main target splash has been added to direct damage
    assert actual.direct_damage[actual.outcome == 0].min() == 1
    assert actual.direct_damage[actual.outcome == 0].max() == 1
    assert actual.splash_damage[actual.outcome == 0].min() == 1
    assert actual.splash_damage[actual.outcome == 0].max() == 1

    assert actual.total_damage[actual.outcome == 1].min() == 1 + 4
    assert actual.total_damage[actual.outcome == 1].max() == 8 + 4
    assert actual.total_damage[actual.outcome == 2].min() == 1 * 2 + 4
    assert actual.total_damage[actual.outcome == 2].max() == 8 * 2 + 4


def test_splash_damage_no_direct():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 0, 0, 1, splash=True),
    )
    assert actual.total_damage[actual.outcome == -1].sum() == 0

    # Main target splash has been added to direct damage, even if there's no
    # direct damage anyway
    assert actual.direct_damage[actual.outcome > -1].min() == 1
    assert actual.direct_damage[actual.outcome > -1].max() == 1
    assert actual.splash_damage[actual.outcome > -1].min() == 1
    assert actual.splash_damage[actual.outcome > -1].max() == 1
    assert actual.total_damage[actual.outcome > -1].min() == 2
    assert actual.total_damage[actual.outcome > -1].max() == 2


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
    assert 32 < actual.total_damage[actual.outcome == 2].max() <= 36


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
        Damage("fire", 0, 0, 1),
        weaknesses={"fire": 10},
    )
    # Weaknesses don't double on a crit
    assert np.unique(actual.total_damage).tolist() == [0, 11, 12]


def test_resistances():
    actual = damage(
        check(6, DC=15),
        Damage("fire", 1, 6),
        resistances={"fire": 5},
    )
    assert np.unique(actual.total_damage[actual.outcome == 1]).tolist() == [0, 1]
    # Resistances don't double on a crit
    assert actual.total_damage[actual.outcome == 2].max() == 7


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
    set_size(10_000)

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
    actual = damage(check(6, DC=15), Damage("fire", 1, 4, basic_save=True))
    assert actual.direct_damage.dtype.kind == "i"
    assert actual.total_damage.dtype.kind == "i"
    assert actual.total_damage[actual.outcome == -1].max() == 8
    assert actual.total_damage[actual.outcome == 0].max() == 4
    assert np.unique(actual.total_damage[actual.outcome == 1]).tolist() == [0, 1, 2]
    assert actual.total_damage[actual.outcome == 2].max() == 0
