from __future__ import annotations

from xarray import DataArray
from xarray.testing import assert_equal

from pathfinder2e_stats import level2rank, rank2level


def test_level2rank():
    assert level2rank(-1) == 0
    assert level2rank(0) == 0
    assert level2rank(1) == 1
    assert level2rank(2) == 1
    assert level2rank(3) == 2
    assert isinstance(level2rank(1), int)

    assert_equal(
        level2rank(DataArray([1, 2, 3])),
        DataArray([1, 1, 2]),
    )


def test_rank2level():
    assert rank2level(3) == 6
    assert isinstance(rank2level(1), int)

    assert_equal(
        rank2level(DataArray([1, 2, 3])),
        DataArray([2, 4, 6]),
    )


def test_level2rank_dedication():
    level = list(range(1, 21))
    expect = [0, 0, 0, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8]
    assert_equal(
        level2rank(DataArray(level), dedication=True),
        DataArray(expect),
    )
    for level_i, expect_i in zip(level, expect, strict=True):
        actual_i = level2rank(level_i, dedication=True)
        assert actual_i == expect_i
        assert isinstance(actual_i, int)


def test_rank2level_dedication():
    level = list(range(1, 9))
    expect = [4, 6, 8, 12, 14, 16, 18, 20]
    assert_equal(
        rank2level(DataArray(level), dedication=True),
        DataArray(expect),
    )
    for level_i, expect_i in zip(level, expect, strict=True):
        actual_i = rank2level(level_i, dedication=True)
        assert actual_i == expect_i
        assert isinstance(actual_i, int)
