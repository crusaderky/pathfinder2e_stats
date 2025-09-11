from __future__ import annotations

from functools import partial

import pytest
from xarray import DataArray, Dataset
from xarray.testing import assert_equal

from pathfinder2e_stats import level2rank, rank2level, set_config
from pathfinder2e_stats.tools import _parse_independent_dependent_dims


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


def test_parse_independent_dependent_dims():
    ds = Dataset({"DC": ("foo", [1, 2])})
    p = partial(_parse_independent_dependent_dims, "check", ds)

    assert p(["foo"], []) == {"foo": 2}
    assert p(("foo",), []) == {"foo": 2}
    assert p({"foo"}, []) == {"foo": 2}
    assert p({"foo": None}, []) == {"foo": 2}
    assert p({"foo": 2}, []) == {"foo": 2}
    assert p({"foo": 2, "bar": 3}, []) == {"foo": 2, "bar": 3}
    assert p({"foo": None, "bar": 3}, []) == {"foo": 2, "bar": 3}
    assert p([], ["foo"]) == {}
    assert p([], ("foo",)) == {}
    assert p([], {"foo"}) == {}

    with pytest.raises(
        ValueError,
        match=r"foo.*must be listed in either independent_dims or dependent_dims",
    ):
        p([], [])
    with pytest.raises(ValueError, match=r"foo.*already exists with size 2"):
        p({"foo": 3}, [])
    with pytest.raises(ValueError, match=r"foo.*both independent and dependent"):
        p(["foo"], ["foo"])
    with pytest.raises(KeyError, match="notfound"):
        p(["foo", "notfound"], ())
    with pytest.raises(KeyError, match="notfound"):
        p({"foo": None, "notfound": None}, ())
    with pytest.raises(KeyError, match="notfound"):
        p([], ["foo", "notfound"])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*parameter `independent_dims`"
    ):
        p(["foo", "roll"], [])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*parameter `dependent_dims`"
    ):
        p([], ["foo", "roll"])


def test_parse_independent_dependent_dims_config_check():
    ds = Dataset({"DC": ("foo", [1, 2])})
    p = partial(_parse_independent_dependent_dims, "check", ds)

    set_config(check_independent_dims=["foo"])
    assert p([], []) == {"foo": 2}
    set_config(check_independent_dims=("foo",))
    assert p([], []) == {"foo": 2}
    set_config(check_independent_dims={"foo"})
    assert p([], []) == {"foo": 2}

    # Unlike with the parameter, extra dims in the config are ignored
    set_config(check_independent_dims=["foo", "bar"])
    assert p([], []) == {"foo": 2}

    # Override config
    assert p(["foo"], []) == {"foo": 2}
    assert p({"foo": None}, []) == {"foo": 2}
    assert p([], ["foo"]) == {}

    set_config(check_independent_dims=[], check_dependent_dims=["foo", "bar"])
    assert p([], []) == {}
    assert p(["foo"], []) == {"foo": 2}  # Override
    assert p({"foo": None, "bar": 3}, []) == {"foo": 2, "bar": 3}  # Override

    set_config(check_independent_dims=["foo"], check_dependent_dims=[])
    assert p([], []) == {"foo": 2}

    set_config(check_independent_dims=["foo"], check_dependent_dims=["foo"])
    with pytest.raises(
        ValueError, match=r"foo.*check_independent_dims.*check_dependent_dims"
    ):
        p([], [])

    set_config(check_independent_dims=["foo", "roll"], check_dependent_dims=[])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*check_independent_dims"
    ):
        p([], [])

    set_config(check_independent_dims=["foo"], check_dependent_dims=["roll"])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*check_dependent_dims"
    ):
        p([], [])


def test_parse_independent_dependent_dims_config_damage():
    ds = Dataset({"DC": ("foo", [1, 2])})
    p = partial(_parse_independent_dependent_dims, "damage", ds)

    set_config(damage_independent_dims=["foo"])
    assert p([], []) == {"foo": 2}
    set_config(damage_independent_dims=("foo",))
    assert p([], []) == {"foo": 2}
    set_config(damage_independent_dims={"foo"})
    assert p([], []) == {"foo": 2}

    # Unlike with the parameter, extra dims in the config are ignored
    set_config(damage_independent_dims=["foo", "bar"])
    assert p([], []) == {"foo": 2}

    # Override config
    assert p(["foo"], []) == {"foo": 2}
    assert p({"foo": None}, []) == {"foo": 2}
    assert p([], ["foo"]) == {}

    set_config(damage_independent_dims=[], damage_dependent_dims=["foo", "bar"])
    assert p([], []) == {}
    assert p(["foo"], []) == {"foo": 2}  # Override
    assert p({"foo": None, "bar": 3}, []) == {"foo": 2, "bar": 3}  # Override

    set_config(damage_independent_dims=["foo"], damage_dependent_dims=[])
    assert p([], []) == {"foo": 2}

    set_config(damage_independent_dims=["foo"], damage_dependent_dims=["foo"])
    with pytest.raises(
        ValueError, match=r"foo.*damage_independent_dims.*damage_dependent_dims"
    ):
        p([], [])

    set_config(damage_independent_dims=["foo", "roll"], damage_dependent_dims=[])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*damage_independent_dims"
    ):
        p([], [])

    set_config(damage_independent_dims=["foo"], damage_dependent_dims=["roll"])
    with pytest.raises(
        ValueError, match=r"roll.*always independent.*damage_dependent_dims"
    ):
        p([], [])


def test_parse_independent_dependent_dims_config_cross():
    ds = Dataset({"x": ("foo", [1, 2]), "y": ("bar", [3, 4, 5])})
    set_config(
        check_independent_dims=["foo"],
        check_dependent_dims=["bar"],
        damage_independent_dims=["bar"],
        damage_dependent_dims=["foo"],
    )
    assert _parse_independent_dependent_dims("check", ds, [], []) == {"foo": 2}
    assert _parse_independent_dependent_dims("damage", ds, [], []) == {"bar": 3}
