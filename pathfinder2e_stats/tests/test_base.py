from __future__ import annotations

from pathfinder2e_stats import DoS, roll, set_size


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
