from __future__ import annotations

from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import DoS, level2rank, rank2level, roll, set_size


def test_stable_rng():
    assert roll(1, 100)[:5].values.tolist() == [45, 48, 65, 68, 68]


def test_set_size():
    assert roll(1, 20).shape == (1000,)
    n = set_size(10)
    assert n == 1000
    assert roll(1, 20).shape == (10,)
    n = set_size(20)
    assert n == 10


def test_DoS_str():
    assert str(DoS.critical_success) == "Critical success"


def test_DoS_legend():
    assert DoS.legend() == {
        -2: "No roll",
        -1: "Critical failure",
        0: "Failure",
        1: "Success",
        2: "Critical success",
    }


def test_level2rank():
    assert level2rank(-1) == 0
    assert level2rank(0) == 0
    assert level2rank(1) == 1
    assert level2rank(2) == 1
    assert level2rank(3) == 2

    assert_equal(
        level2rank(DataArray([1, 2, 3])),
        DataArray([1, 1, 2]),
    )


def test_rank2level():
    assert rank2level(3) == 6

    assert_equal(
        rank2level(DataArray([1, 2, 3])),
        DataArray([2, 4, 6]),
    )
