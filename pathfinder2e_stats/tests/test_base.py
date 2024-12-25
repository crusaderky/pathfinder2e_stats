from __future__ import annotations

from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import level2rank, rank2level, roll, seed, set_size


def test_seed():
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]
    assert roll(1, 100)[:5].values.tolist() == [56, 9, 19, 88, 45]
    seed(0)
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]
    seed(1)
    assert roll(1, 100)[:5].values.tolist() == [48, 52, 76, 96, 4]


def test_seed_fixture():
    """Test that a global pytest fixture resets the seed before each test"""
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]


def test_set_size():
    assert roll(1, 20).shape == (1000,)
    n = set_size(10)
    assert n == 1000
    assert roll(1, 20).shape == (10,)
    n = set_size(20)
    assert n == 10


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


def test_level2rank_dedication():
    level = list(range(1, 21))
    expect = [0, 0, 0, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8]
    assert_equal(
        level2rank(DataArray(level), dedication=True),
        DataArray(expect),
    )
    for level_i, expect_i in zip(level, expect, strict=False):
        actual_i = level2rank(level_i, dedication=True)
        assert actual_i == expect_i
        assert isinstance(actual_i, int)


def test_rank2level():
    assert rank2level(3) == 6

    assert_equal(
        rank2level(DataArray([1, 2, 3])),
        DataArray([2, 4, 6]),
    )
