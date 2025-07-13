from __future__ import annotations

import pytest

from pathfinder2e_stats import config


@pytest.fixture(scope="session", autouse=True)
def set_roll_size():
    config._roll_size_default = 1000


@pytest.fixture(autouse=True)
def reset_config():
    config._config.__dict__.clear()
    yield
    config._config.__dict__.clear()
