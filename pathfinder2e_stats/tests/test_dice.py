from __future__ import annotations

import numpy as np
import pytest
from xarray.testing import assert_identical

from pathfinder2e_stats import d20, roll, set_size


def test_stable_rng():
    assert roll(1, 100)[:5].values.tolist() == [45, 48, 65, 68, 68]


def test_set_size():
    assert roll(1, 20).shape == (1000,)
    n = set_size(10)
    assert n == 1000
    assert roll(1, 20).shape == (10,)
    n = set_size(20)
    assert n == 10


def test_roll():
    r = roll(1, 100)
    assert r.shape == (1000,)
    assert r.dims == ("roll",)
    assert r.dtype.kind == "i"
    assert r.min() == 1
    assert r.max() == 100

    r = roll(2, 6, 10)
    assert np.unique(r).tolist() == list(range(12, 23))
    assert 16 < r.mean() < 18


def test_roll_dims():
    r = roll(2, 6, 3, dims={"foo": 2, "bar": 3})
    assert r.shape == (1000, 2, 3)
    assert r.dims == ("roll", "foo", "bar")


def test_roll_floor():
    r = roll(2, 6, -10)
    assert np.unique(r).tolist() == [0, 1, 2]

    r = roll(2, 6, -12)
    assert (r == 0).all()


@pytest.mark.parametrize(
    "s,count,faces,bonus",
    [
        ("4d6+3", 4, 6, 3),
        ("d20", 1, 20, 0),
        ("d100-5", 1, 100, -5),
        ("123d2+456", 123, 2, 456),
    ],
)
def test_roll_str(s, count, faces, bonus):
    np.random.seed(0)
    a = roll(count, faces, bonus)
    np.random.seed(0)
    b = roll(s)
    assert_identical(a, b)


def test_roll_bad_params():
    with pytest.raises(TypeError, match="required positional argument: 'count_or_s'"):
        roll()
    with pytest.raises(TypeError, match="required positional argument: 'faces'"):
        roll(1)
    with pytest.raises(ValueError, match="Could not parse dice roll"):
        roll("bad")
    with pytest.raises(ValueError, match="Could not parse dice roll"):
        roll("2d")
    with pytest.raises(ValueError, match="Could not parse dice roll"):
        roll("+5")


def test_d20():
    r = d20()
    assert r.dims == ("roll",)
    assert r.shape == (1000,)
    assert np.unique(r).tolist() == list(range(1, 21))


def test_d20_dims():
    r = d20(dims={"x": 2})
    assert r.dims == ("roll", "x")
    assert r.shape == (1000, 2)
    assert np.unique(r).tolist() == list(range(1, 21))


def test_d20_fortune():
    r1 = d20()
    r2 = d20(fortune=True)
    r3 = d20(misfortune=True)
    for r in r1, r2, r3:
        assert np.unique(r).tolist() == list(range(1, 21))

    assert 450 < (r1 > 10).sum() < 550
    assert 700 < (r2 > 10).sum() < 800
    assert 200 < (r3 > 10).sum() < 300

    with pytest.raises(ValueError, match="both fortune and misfortune"):
        d20(fortune=True, misfortune=True)


def test_d20_fortune_dims():
    r = d20(fortune=True, dims={"x": 4})
    assert r.dims == ("roll", "x")
    assert r.shape == (1000, 4)
    for i in range(4):
        assert 700 < (r.isel(x=i) > 10).sum() < 800
