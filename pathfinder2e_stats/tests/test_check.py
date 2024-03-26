from __future__ import annotations

import numpy as np
import pytest
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import DoS, check, map_outcome


def test_DoS_str():
    assert str(DoS.critical_success) == "Critical success"


@pytest.mark.parametrize("k", ["evasion", "juggernaut", "resolve", "risky_surgery"])
def test_map_outcome_success_to_crit_success(k):
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(
        map_outcome(x, **{k: True}),
        DataArray([-2, -1, 0, 2, 2]),
    )

    assert_equal(
        map_outcome(x, **{k: DataArray([True, False], dims=["x"])}),
        DataArray([[-2, -2], [-1, -1], [0, 0], [2, 1], [2, 2]], dims=["dim_0", "x"]),
    )


def test_map_outcome_to_value():
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(
        map_outcome(x, {1: 10, 2: 20}),
        DataArray([0, 0, 0, 10, 20]),
    )

    actual = map_outcome(x, {1: True, 2: True})
    assert_equal(actual, DataArray([False, False, False, True, True]))
    assert actual.dtype == bool

    actual = map_outcome(x, {1: 3.0})
    assert_equal(actual, DataArray([0.0, 0.0, 0.0, 3.0, 0]))
    assert actual.dtype.kind == "f"

    assert_equal(
        map_outcome(x, {1: DataArray([10, 20], dims=["y"])}),
        DataArray(
            [
                [0, 0],
                [0, 0],
                [0, 0],
                [10, 20],
                [0, 0],
            ],
            dims=["dim_0", "y"],
        ),
    )


def test_map_outcome_incapacitation():
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(
        map_outcome(x, incapacitation=True),
        DataArray([-2, 0, 1, 2, 2]),  # Preserve no_roll
    )
    assert_equal(
        map_outcome(x, incapacitation=-1),
        DataArray([-2, -1, -1, 0, 1]),  # Preserve no_roll
    )
    assert_equal(
        map_outcome(
            x,
            incapacitation=DataArray([-1, 0, 1], dims=["y"]),
        ),
        DataArray(
            [
                [-2, -2, -2],  # Preserve no_roll
                [-1, -1, 0],
                [-1, 0, 1],
                [0, 1, 2],
                [1, 2, 2],
            ],
            dims=["dim_0", "y"],
        ),
    )


def test_map_outcome_clip():
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(
        map_outcome(x, allow_critical_failure=False),
        DataArray([-2, 0, 0, 1, 2]),
    )
    assert_equal(
        map_outcome(x, allow_failure=False),
        DataArray([-2, -1, 1, 1, 2]),
    )
    assert_equal(
        map_outcome(x, allow_critical_success=False),
        DataArray([-2, -1, 0, 1, 1]),
    )
    assert_equal(
        map_outcome(x, allow_critical_failure=False, allow_failure=False),
        DataArray([-2, 1, 1, 1, 2]),
    )
    assert_equal(
        map_outcome(x, allow_critical_success=False, incapacitation=True),
        DataArray([-2, 0, 1, 1, 1]),
    )
    assert_equal(
        map_outcome(x, allow_critical_failure=False, incapacitation=-1),
        DataArray([-2, 0, 0, 0, 1]),
    )


def test_map_outcome_noop():
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(map_outcome(x), x)
    assert_equal(map_outcome(x, {-2: -2, -1: -1, 0: 0, 1: 1, 2: 2}), x)


def test_map_outcome_empty_map():
    assert_equal(
        map_outcome(DataArray([-2, -1, 0, 1, 2]), {}),
        DataArray([0, 0, 0, 0, 0]),
    )


def test_map_outcome_string():
    assert_equal(
        map_outcome(DataArray([-2, -1, 0, 1, 2]), {1: "X", 2: "YY"}),
        DataArray(["", "", "", "X", "YY"]),
    )


def test_map_outcome_sequence():
    assert_equal(
        map_outcome(
            DataArray([-1, 0, 1, 2]),
            [
                # In case of multiple matches, leftmost wins
                (DataArray([0, 1], dims=["x"]), 10),
                (1, 20),
            ],
        ),
        DataArray(
            [
                [0, 0],
                [10, 0],
                [20, 10],
                [0, 0],
            ],
            dims=["dim_0", "x"],
        ),
    )


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
            -2: "No roll",
            -1: "Critical failure",
            0: "Failure",
            1: "Success",
            2: "Critical success",
        },
        "misfortune": False,
    }

    assert ds.natural.dims == ("roll",)
    assert ds.natural.dtype.kind == "i"
    assert np.unique(ds.natural).tolist() == list(range(1, 21))

    assert ds.outcome.dims == ("roll",)
    assert ds.outcome.dtype.kind == "i"
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


def test_check_map_outcome_bool():
    ds = check(DC=9, juggernaut=True)
    assert_equal(ds.original_outcome == 2, ds.natural >= 19)
    assert_equal(ds.outcome == 2, ds.natural >= 9)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 2]
    assert ds.attrs["juggernaut"] is True


def test_check_map_outcome_int():
    ds = check(DC=9, incapacitation=-1)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1]
    assert ds.attrs["incapacitation"] == -1


def test_check_map_outcome_array():
    ds = check(
        DC=9,
        juggernaut=DataArray([False, True], dims=["x"]),
        incapacitation=DataArray([-1, 0, 1], dims=["y"]),
    )
    assert ds.original_outcome.sizes == {"roll": 1000}
    assert ds.outcome.sizes == {"roll": 1000, "x": 2, "y": 3}
    assert ds.attrs["juggernaut"] == "varies"
    assert ds.attrs["incapacitation"] == "varies"


def test_chain_check_map_outcome():
    ds = map_outcome(check(DC=9), {2: 10})
    assert_equal(ds.original_outcome == 2, ds.natural >= 19)
    assert_equal(ds.outcome == 10, ds.natural >= 19)
    assert np.unique(ds.outcome).tolist() == [0, 10]


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
