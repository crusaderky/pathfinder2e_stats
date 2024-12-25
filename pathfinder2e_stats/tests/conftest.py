from __future__ import annotations

import pytest

from pathfinder2e_stats.base import seed, set_size


@pytest.fixture(autouse=True)
def init_rng():
    seed(0)


@pytest.fixture(autouse=True)
def init_size():
    prev = set_size(1000)
    yield
    set_size(prev)
