from __future__ import annotations

import numpy as np
import pytest
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import DoS, check, map_outcomes


def test_map_outcomes_basic():
    assert map_outcomes(None) == {}
    r = map_outcomes({-1: 1, DoS.success: DoS.critical_success})
    assert r == {-1: 1, 1: 2}
    assert all(isinstance(k, DoS) for k in r)
    assert all(isinstance(v, DoS) for v in r.values())

    with pytest.raises(ValueError):
        map_outcomes({-2: 0})


def test_map_outcomes_kwargs():
    assert map_outcomes(evasion=True) == {1: 2}
    assert map_outcomes(juggernaut=True) == {1: 2}
    assert map_outcomes(resolve=True) == {1: 2}
    assert map_outcomes(risky_surgery=True) == {1: 2}

    assert map_outcomes(incapacitation=False) == {}
    assert map_outcomes(incapacitation=0) == {}
    assert map_outcomes(incapacitation=True) == {-1: 0, 0: 1, 1: 2}
    assert map_outcomes(incapacitation=1) == {-1: 0, 0: 1, 1: 2}
    assert map_outcomes(incapacitation=-1) == {2: 1, 1: 0, 0: -1}

    assert map_outcomes(allow_critical_failure=False) == {-1: 0}
    assert map_outcomes(incapacitation=-1, allow_critical_failure=False) == {
        -1: 0,
        1: 0,
        2: 1,
    }
    assert map_outcomes(allow_failure=False) == {-1: 1, 0: 1}
    assert map_outcomes(incapacitation=-1, allow_failure=False) == {-1: 1, 0: 1, 2: 1}
    assert map_outcomes(allow_critical_success=False) == {2: 1}
    assert map_outcomes(incapacitation=True, allow_critical_success=False) == {
        -1: 0,
        0: 1,
        2: 1,
    }
    assert map_outcomes(allow_failure=False, allow_critical_failure=False) == {
        -1: 1,
        0: 1,
    }
    assert map_outcomes(allow_critical_failure=False, allow_critical_success=False) == {
        -1: 0,
        2: 1,
    }


def test_map_outcomes_removes_identity():
    assert map_outcomes({0: 0, DoS.success: DoS.success}) == {}
    assert map_outcomes(evasion=True, allow_critical_success=False) == {2: 1}


def test_check_basic():
    ds = check(DC=7)
    assert ds.bonus == 0
    assert ds.DC == 7
    assert ds.sizes == {"roll": 1000}
    assert ds.attrs == {
        "fortune": False,
        "hero_point": False,
        "keen": False,
        "legend": {
            -1: "critical_failure",
            0: "failure",
            1: "success",
            2: "critical_success",
        },
        "map_outcomes": {},
        "misfortune": False,
    }

    assert ds.natural.dims == ("roll",)
    assert ds.natural.dtype == "i1"
    assert np.unique(ds.natural).tolist() == list(range(1, 21))

    assert ds.outcome.dims == ("roll",)
    assert ds.outcome.dtype == "i1"
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1, 2]
    assert_equal(ds.outcome == -1, ds.natural == 1)
    assert_equal(ds.outcome == 0, (ds.natural > 1) & (ds.natural < 7))
    assert_equal(ds.outcome == 1, (ds.natural >= 7) & (ds.natural < 17))
    assert_equal(ds.outcome == 2, ds.natural >= 17)


def test_check_nat1():
    ds = check(+10, DC=25)
    assert_equal(ds.outcome == -1, ds.natural < 6)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1, 2]

    ds = check(+10, DC=12)
    assert_equal(ds.outcome == -1, ds.natural == 1)
    assert np.unique(ds.outcome).tolist() == [-1, 1, 2]

    ds = check(+10, DC=10)
    assert_equal(ds.outcome == 0, ds.natural == 1)
    assert np.unique(ds.outcome).tolist() == [0, 1, 2]

    ds = check(+10, DC=0)
    assert_equal(ds.outcome == 1, ds.natural == 1)
    assert np.unique(ds.outcome).tolist() == [1, 2]


def test_check_nat20():
    ds = check(+10, DC=40)
    assert_equal(ds.outcome == 0, ds.natural == 20)
    assert np.unique(ds.outcome).tolist() == [-1, 0]

    ds = check(+10, DC=31)
    assert_equal(ds.outcome == 1, ds.natural == 20)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1]

    ds = check(+10, DC=30)
    assert_equal(ds.outcome == 2, ds.natural == 20)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 2]

    ds = check(+10, DC=15)
    assert_equal(ds.outcome == 2, ds.natural >= 15)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1, 2]


def test_check_keen():
    # keen only promotes success to crit success
    ds = check(+10, DC=40, keen=True)
    assert_equal(ds.outcome == 0, ds.natural == 20)
    assert np.unique(ds.outcome).tolist() == [-1, 0]

    ds = check(+10, DC=31, keen=True)
    assert_equal(ds.outcome == 1, ds.natural == 20)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1]

    ds = check(+10, DC=25, keen=True)
    assert_equal(ds.outcome == 2, ds.natural >= 19)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1, 2]


def test_check_fortune():
    r1 = check(DC=10)
    r2 = check(DC=10, fortune=True)
    r3 = check(DC=10, misfortune=True)
    for r in r1, r2, r3:
        assert np.unique(r.natural).tolist() == list(range(1, 21))
        assert np.unique(r.outcome).tolist() == [-1, 0, 1, 2]

    assert 450 < (r1.natural > 10).sum() < 550
    assert 700 < (r2.natural > 10).sum() < 800
    assert 200 < (r3.natural > 10).sum() < 300
    assert 450 < (r1.outcome > 0).sum() < 550
    assert 700 < (r2.outcome > 0).sum() < 800
    assert 200 < (r3.outcome > 0).sum() < 300

    with pytest.raises(ValueError, match="both fortune and misfortune"):
        check(DC=20, fortune=True, misfortune=True)


def test_check_map_outcomes():
    ds = check(DC=10, evasion=True)
    assert_equal(ds.outcome == 2, ds.natural >= 10)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 2]
    assert ds.attrs["map_outcomes"] == {"success": "critical_success"}

    ds = check(
        DC=10, juggernaut=True, map_outcomes={1: 0}, allow_critical_failure=False
    )
    assert_equal(ds.outcome == 2, ds.natural >= 10)
    assert_equal(ds.outcome == 0, ds.natural < 10)
    assert np.unique(ds.outcome).tolist() == [0, 2]


def test_check_map_outcomes_no_multiple_bumps():
    """Test that we're NOT doing::

        for k, v in map_outcomes.items():
           out = out.where(out != k, v)

    which e.g. would cause incapacitation to promote
    critical failures to critical success
    """
    ds = check(DC=15, incapacitation=True)
    assert_equal(ds.outcome == 0, ds.natural < 6)
    assert_equal(ds.outcome == 1, (ds.natural >= 6) & (ds.natural < 15))
    assert_equal(ds.outcome == 2, ds.natural >= 15)
    assert np.unique(ds.outcome).tolist() == [0, 1, 2]


def test_check_map_to_failure():
    ds = check(DC=10, map_outcomes={-1: 0, 1: 0, 2: 0})
    assert ds.sizes == {"roll": 1000}
    assert ds.outcome.shape == (1000,)
    assert ds.outcome.dtype == "i1"
    assert (ds.outcome == 0).all()


@pytest.mark.parametrize(
    "hp,attr,lt",
    [
        (False, False, None),
        (-1, "critical_failure", 6),
        (DoS.failure, "failure", 15),
        (0, "failure", 15),
        (1, "success", 20),
    ],
)
def test_heropoint(hp, attr, lt):
    ds = check(+5, DC=20, hero_point=hp)
    assert ds.attrs["hero_point"] == attr
    assert ds.outcome.shape == (1000,)
    if hp is False:
        assert "use_hero_point" not in ds.variables
        assert ds.sizes == {"roll": 1000}
    else:
        assert ds.sizes == {"roll": 1000, "hp_reroll": 2}
        assert ds.natural.shape == (1000, 2)
        assert ds.use_hero_point.shape == (1000,)
        assert ds.use_hero_point.dtype == bool

        assert_equal(ds.use_hero_point, ds.natural[:, 0] < lt)

        ds_roll0 = ds.sel(roll=~ds.use_hero_point)
        assert_equal(ds_roll0.outcome >= 1, ds_roll0.natural[:, 0] >= 15)

        ds_roll1 = ds.sel(roll=ds.use_hero_point)
        assert_equal(ds_roll1.outcome >= 1, ds_roll1.natural[:, 1] >= 15)


def test_check_array_input():
    bonus = DataArray([3, 5], dims=["PC"], coords={"PC": ["Alice", "Bob"]})
    DC = DataArray(
        [15, 16, 17],
        dims=["monster"],
        coords={"monster": ["Bugbear", "Skeleton", "Goblin"]},
    )
    ds = check(bonus, DC=DC)

    assert ds.sizes == {"roll": 1000, "PC": 2, "monster": 3}
    assert_equal(ds.PC, bonus.PC)
    assert_equal(ds.monster, DC.monster)
    assert_equal(ds.bonus, bonus)
    assert_equal(ds.DC, DC)
    assert ds.natural.dims == ("roll",)
    assert ds.outcome.dims == ("roll", "PC", "monster")
    assert (
        ds.sel(PC="Alice", monster="Goblin").outcome.mean()
        < ds.sel(PC="Alice", monster="Bugbear").outcome.mean()
    )
    assert (
        ds.sel(PC="Alice", monster="Goblin").outcome.mean()
        < ds.sel(PC="Bob", monster="Goblin").outcome.mean()
    )
