from __future__ import annotations

import numpy as np
import pytest
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import DoS, check, map_outcome, outcome_counts, set_size


def test_DoS_str():
    assert str(DoS.critical_success) == "Critical success"


def test_map_outcome_success_to_crit_success():
    x = DataArray([-2, -1, 0, 1, 2])
    assert_equal(
        map_outcome(x, evasion=True),
        DataArray([-2, -1, 0, 2, 2]),
    )

    assert_equal(
        map_outcome(x, evasion=DataArray([True, False], dims=["x"])),
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
        "perfected_form": False,
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


def test_check_keen_array():
    r = check(DC=11, keen=DataArray([False, True], dims=["keen"]))
    assert r.natural.sizes == {"roll": 1000}
    assert r.outcome.sizes == {"keen": 2, "roll": 1000}
    r = r.isel(roll=(r.natural == 19))
    assert (r.outcome.isel(keen=0) == DoS.success).all()
    assert (r.outcome.isel(keen=1) == DoS.critical_success).all()
    assert r.attrs["keen"] == "varies"


def test_check_fortune():
    r1 = check(DC=11)
    r2 = check(DC=11, fortune=True)
    r3 = check(DC=11, misfortune=True)
    r4 = check(DC=11, fortune=True, misfortune=True)
    for r in r1, r2, r3:
        assert np.unique(r.natural).tolist() == list(range(1, 21))
        assert np.unique(r.outcome).tolist() == [-1, 0, 1, 2]

    assert r1.attrs["fortune"] is False
    assert r1.attrs["misfortune"] is False
    assert r2.attrs["fortune"] is True
    assert r2.attrs["misfortune"] is False
    assert r3.attrs["fortune"] is False
    assert r3.attrs["misfortune"] is True
    assert r4.attrs["fortune"] is True
    assert r4.attrs["misfortune"] is True

    assert 0.45 < (r1.natural > 10).mean() < 0.55
    assert 0.45 < (r1.outcome > 0).mean() < 0.55
    assert 0.7 < (r2.natural > 10).mean() < 0.8
    assert 0.7 < (r2.outcome > 0).mean() < 0.8
    assert 0.2 < (r3.natural > 10).mean() < 0.3
    assert 0.2 < (r3.outcome > 0).mean() < 0.3
    # Fortune and misfortune cancel each other out
    assert 0.45 < (r4.natural > 10).mean() < 0.55
    assert 0.45 < (r4.outcome > 0).mean() < 0.55


def test_check_fortune_array():
    fortune = DataArray([False, True], dims=["f"], coords={"f": [False, True]})
    r = check(DC=11, fortune=fortune, misfortune=fortune.rename({"f": "m"}))
    assert r.sizes == {"f": 2, "m": 2, "roll": 1000}
    assert r.natural.dims == r.outcome.dims == ("f", "m", "roll")
    assert r.attrs["fortune"] == "varies"
    assert r.attrs["misfortune"] == "varies"


def test_check_map_outcome_bool():
    ds = check(DC=9, evasion=True)
    assert_equal(ds.original_outcome == 2, ds.natural >= 19)
    assert_equal(ds.outcome == 2, ds.natural >= 9)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 2]
    assert ds.attrs["evasion"] is True


def test_check_map_outcome_int():
    ds = check(DC=9, incapacitation=-1)
    assert np.unique(ds.outcome).tolist() == [-1, 0, 1]
    assert ds.attrs["incapacitation"] == -1


def test_check_map_outcome_array():
    ds = check(
        DC=9,
        evasion=DataArray([False, True], dims=["x"]),
        incapacitation=DataArray([-1, 0, 1], dims=["y"]),
    )
    assert ds.original_outcome.sizes == {"roll": 1000}
    assert ds.outcome.sizes == {"roll": 1000, "x": 2, "y": 3}
    assert ds.attrs["evasion"] == "varies"
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
def test_hero_point(hp, attr, lt):
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

        assert_equal(
            ds.use_hero_point,
            ds.natural.sel(hp_reroll="original", drop=True) < lt,
        )

        ds_roll0 = ds.sel(roll=~ds.use_hero_point)
        assert_equal(
            ds_roll0.outcome >= 1,
            ds_roll0.natural.sel(hp_reroll="original", drop=True) >= 15,
        )

        ds_roll1 = ds.sel(roll=ds.use_hero_point)
        assert_equal(
            ds_roll1.outcome >= 1,
            ds_roll1.natural.sel(hp_reroll="hero point", drop=True) >= 15,
        )


def test_hero_point_with_fortune():
    """Hero point is a fortune effect; can't use it when there's another already,
    e.g. Sure Strike
    """
    ds = check(DC=11, hero_point=DoS.failure)
    assert ds.outcome.shape == (1000,)
    assert 0.7 < (ds.outcome >= DoS.success).mean() < 0.8
    assert 0.45 < ds.use_hero_point.mean() < 0.55

    for hero_point in (False, DoS.failure):
        # Disallow hero point
        ds = check(DC=11, hero_point=hero_point, fortune=True)
        assert ds.outcome.shape == (1000,)
        assert 0.7 < (ds.outcome >= DoS.success).mean() < 0.8
        if hero_point is not False:
            assert not ds.use_hero_point.any()

    ds = check(DC=11, misfortune=True)
    assert ds.outcome.shape == (1000,)
    assert 0.2 < (ds.outcome >= DoS.success).mean() < 0.3

    # It's debated how hero points and misfortune interact:
    # https://paizo.com/threads/rzs43lwf?Hero-Points-and-Misfortune-Effects
    # This library implements rolling twice, both times with misfortune.
    ds = check(DC=11, misfortune=True, hero_point=DoS.failure)
    assert ds.outcome.shape == (1000,)
    assert 0.4 < (ds.outcome >= DoS.success).mean() < 0.5
    assert 0.7 < ds.use_hero_point.mean() < 0.8


def test_perfected_form():
    # Inconsequential, if you take 10 it's still a critical failure
    ds = check(+0, DC=20, perfected_form=True)
    assert ds.attrs["perfected_form"] is True
    assert ds.outcome.shape == (1000,)
    assert ds.outcome.min() == DoS.critical_failure
    assert ds.outcome.max() == DoS.critical_success

    # Can discard roll and take 19, but keep roll if better
    ds = check(+9, DC=20, perfected_form=True)
    assert ds.outcome.min() == DoS.failure
    assert ds.outcome.max() == DoS.critical_success

    # Can discard roll and take 20, but keep roll if better
    ds = check(+10, DC=20, perfected_form=True)
    assert ds.outcome.min() == DoS.success
    assert ds.outcome.max() == DoS.critical_success

    # Can forgo roll and take 30
    ds = check(+20, DC=20, perfected_form=True)
    assert ds.outcome.min() == DoS.critical_success


def test_perfected_form_with_fortune():
    """Disable Perfected Form if fortune is active"""
    set_size(2000)  # With fortune there's a 1/400 chance of crit fail
    ds = check(+10, DC=20, perfected_form=True, fortune=True)
    assert ds.outcome.min() == DoS.critical_failure
    assert ds.outcome.max() == DoS.critical_success


def test_perfected_form_with_hero_point():
    # Don't use HP when Perfected Form is enough to get the outcome you want.
    ds = check(+10, DC=20, perfected_form=True, hero_point=DoS.failure)
    assert ds.outcome.min() == DoS.success
    assert ds.outcome.max() == DoS.critical_success
    assert not ds.use_hero_point.any()

    # When you do use HP, it disables Perfected Form so you can actually get worse.
    ds = check(+10, DC=20, perfected_form=True, hero_point=DoS.success)
    assert ds.outcome.min() == DoS.critical_failure
    assert ds.outcome.max() == DoS.critical_success
    assert ds.use_hero_point.any()


def test_hero_point_with_fortune_array():
    ds = check(
        DC=11,
        hero_point=DataArray(
            [-2, -1, 0, 1, 2], dims=["hp"], coords={"hp": [-2, -1, 0, 1, 2]}
        ),
        fortune=DataArray([False, True], dims=["f"], coords={"f": [False, True]}),
    )
    assert ds.attrs["hero_point"] == "varies"
    assert ds.attrs["fortune"] == "varies"
    assert ds.outcome.sizes == {"roll": 1000, "hp": 5, "f": 2}
    assert ds.use_hero_point.sizes == {"roll": 1000, "hp": 5, "f": 2}
    assert not ds.use_hero_point.sel(f=True).any()
    assert not ds.use_hero_point.sel(hp=-2).any()
    assert 0.03 < ds.use_hero_point.sel(hp=-1, f=False).mean() < 0.06
    assert 0.45 < ds.use_hero_point.sel(hp=0, f=False).mean() < 0.55
    assert 0.93 < ds.use_hero_point.sel(hp=1, f=False).mean() < 0.97
    assert ds.use_hero_point.sel(hp=2, f=False).all()


def test_perfected_form_with_fortune_array():
    set_size(2000)  # With fortune there's a 1/400 chance of crit fail
    ds = check(
        DC=10,
        perfected_form=DataArray([False, True], dims=["pf"]),
        fortune=DataArray([False, True], dims=["f"]),
    )
    assert ds.attrs["perfected_form"] == "varies"
    assert ds.attrs["fortune"] == "varies"
    assert ds.outcome.sizes == {"roll": 2000, "f": 2, "pf": 2}
    # Fortune overrides Perfected Form
    assert ds.outcome.isel(f=1, pf=0).min() == DoS.critical_failure
    assert ds.outcome.isel(f=1, pf=0).max() == DoS.critical_success
    assert ds.outcome.isel(f=1, pf=1).min() == DoS.critical_failure
    assert ds.outcome.isel(f=1, pf=1).max() == DoS.critical_success
    assert ds.outcome.isel(f=0, pf=1).min() == DoS.success
    assert ds.outcome.isel(f=0, pf=1).max() == DoS.critical_success


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


def test_outcome_counts():
    c = check(5, DC=12)
    oc = outcome_counts(c, normalize=False)
    assert oc.dims == ("outcome",)
    assert oc.coords["outcome"][0] == "Critical success"  # success > failure
    assert (
        oc.sel(outcome="Critical success").sum()
        == c.outcome[c.outcome == DoS.critical_success].size
    )

    oc2 = outcome_counts(c.outcome, normalize=False)
    assert_equal(oc, oc2)

    oc3 = outcome_counts(c)  # Defaults to normalize=True
    assert_equal(oc3, oc / c.sizes["roll"])


def test_outcome_counts_extra_dims():
    c = check(5, DC=12, dims={"foo": 3, "bar": 4})
    oc = outcome_counts(c)
    assert oc.dims == ("foo", "bar", "outcome")

    oc2 = outcome_counts(c, dim="foo", new_dim="baz")
    assert oc2.dims == ("roll", "bar", "baz")
