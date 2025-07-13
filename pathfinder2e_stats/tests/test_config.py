from __future__ import annotations

import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from pathfinder2e_stats import get_config, roll, seed, set_config


def assert_seed0():
    """Assert that the random number generator was seeded to zero
    just before calling this function.
    """
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]


def test_seed():
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]
    assert roll(1, 100)[:5].values.tolist() == [56, 9, 19, 88, 45]
    seed(0)
    assert roll(1, 100)[:5].values.tolist() == [86, 64, 52, 27, 31]
    seed(1)
    assert roll(1, 100)[:5].values.tolist() == [48, 52, 76, 96, 4]


def test_seed_fixture():
    """Test that a global pytest fixture resets the seed before each test"""
    assert_seed0()


def test_seed_none():
    """Test that calling seed() with no parameter produces a different sequence."""
    seed(None)
    a = roll(1, 100)
    seed(None)
    b = roll(1, 100)
    assert (a != b).any()


def test_seed_multithreading():
    """Test that new threads are seeded to zero by default."""
    seed(1)
    with ThreadPoolExecutor(1) as executor:
        future = executor.submit(assert_seed0)
        future.result()


def test_seed_multiprocessing():
    """Test that new processes are seeded to zero by default."""
    seed(1)
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(1, mp_context=ctx) as executor:
        future = executor.submit(assert_seed0)
        future.result()


def test_get_config():
    config = get_config()
    assert config == {
        "roll_size": 1000,
        "check_dependent_dims": set(),
        "check_independent_dims": set(),
        "damage_dependent_dims": set(),
        "damage_independent_dims": set(),
    }


def test_tests_reset_config_1():
    """config changes in one test don't impact later tests."""
    set_config(roll_size=123)


def test_tests_reset_config_2():
    """config changes in one test don't impact later tests."""
    assert get_config()["roll_size"] == 1000


def test_roll_size():
    assert get_config()["roll_size"] == 1_000  # Test-specific override
    assert roll(1, 20).shape == (1000,)
    set_config(roll_size=10)
    assert get_config()["roll_size"] == 10
    assert roll(1, 20).shape == (10,)


def test_thread_local_config():
    # Set config in main thread before spawning a new thread
    set_config(roll_size=123)
    with ThreadPoolExecutor(1) as executor:
        future = executor.submit(get_config)
        assert future.result()["roll_size"] == 1000

        # Set config in main thread while another thread is running
        set_config(roll_size=456)
        future = executor.submit(get_config)
        assert future.result()["roll_size"] == 1000

        # Config changed in another thread doesn't impact main
        future = executor.submit(set_config, roll_size=789)
        future.result()
        assert get_config()["roll_size"] == 456
