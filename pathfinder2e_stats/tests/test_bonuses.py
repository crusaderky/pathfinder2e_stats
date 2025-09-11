import pytest
from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import sum_bonuses


@pytest.mark.parametrize(
    "args,expect",
    [
        ((), 0),
        ((("status", 1),), 1),
        ((("status", -1),), -1),
        ((("status", 1), ("item", 2)), 3),  # different type
        ((("status", 1), ("status", 2)), 2),  # max of bonuses
        ((("status", -1), ("status", -2)), -2),  # min of penalties
        ((("status", 5), ("status", -3)), 2),  # bonus + penalty
        ((("untyped", 1), ("untyped", 2)), 3),  # untyped bonuses stack
        ((("untyped", -1), ("untyped", -2)), -3),  # untyped penalties stack
        # Complex example
        (
            (
                ("status", -1),
                ("status", -2),
                ("status", 5),
                ("circumstance", 2),
                ("item", 4),
                ("untyped", 5),
                ("untyped", 6),
                ("proficiency", 15),
                ("ability", 4),
            ),
            39,
        ),
    ],
)
def test_sum_bonuses(args, expect):
    actual = sum_bonuses(*args)
    assert isinstance(actual, int)
    assert actual == expect


def test_sum_bonuses_bad_type():
    with pytest.raises(ValueError, match=r"untyped.*bad"):
        sum_bonuses(("bad", 2))
    with pytest.raises(ValueError, match=r"untyped.*bad"):
        sum_bonuses(("item", 1), ("bad", 2))


def test_sum_bonuses_array():
    actual = sum_bonuses(
        ("item", 1),
        ("status", DataArray([0, 1, 2], dims=["x"], coords={"x": [10, 20, 30]})),
        ("status", DataArray([[3], [4]], dims=["y", "x"], coords={"x": [40]})),
        ("untyped", DataArray([15, 16], dims=["y"])),
    )
    assert isinstance(actual, DataArray)
    assert actual.dtype.kind == "i"
    assert_equal(
        actual,
        DataArray(
            [[16, 17], [17, 18], [18, 19], [19, 21]],
            dims=["x", "y"],
            coords={"x": [10, 20, 30, 40]},
        ),
    )


@pytest.mark.parametrize("x", [DataArray(1), DataArray(1, coords={"foo": "bar"})])
def test_sum_bonuses_scalar_array(x):
    actual = sum_bonuses(("item", x))
    assert isinstance(actual, DataArray)
    assert_equal(actual, x)
