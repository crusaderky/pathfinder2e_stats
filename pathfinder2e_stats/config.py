from __future__ import annotations

import threading
from typing import Any, TypedDict, cast

import numpy as np

_config = threading.local()

# pytest-run-parallell hack to let a fixture override the default roll_size
_roll_size_default: int = 100_000


def rng() -> np.random.Generator:
    """Get the library-global, thread-local random number generator."""
    try:
        return _config.rng
    except AttributeError:
        seed(0)
        return _config.rng


def seed(n: Any | None = None) -> None:
    """Seed the library-global, thread-local random number generator.

    Accepts the same parameter as :func:`numpy.random.default_rng`, which means that
    calling it with no arguments will produce a different random sequence every time.

    By default, the random number generator is seeded to 0 for all new threads. This
    means, for example, that restarting and rerunning the same Jupyter notebook will
    produce identical results, but true multi-threaded applications don't need to worry
    about seeding. However, the side effect is that multi-process and multi-threaded
    applications need to be careful to call :func:`seed` on each thread and process or
    will produce the same sequence of random numbers everywhere.

    See also :func:`seed`.
    """
    _config.rng = np.random.default_rng(n)


class Config(TypedDict):
    """dict returned by :func:`~pathfinder2e_stats.get_config`."""

    #: Number of rolls in all simulations. Default: 100_000.
    roll_size: int


def get_config() -> Config:
    """Return the current configuration settings."""
    d = _config.__dict__.copy()
    d.pop("rng", None)
    d.setdefault("roll_size", _roll_size_default)
    return cast(Config, d)


def set_config(roll_size: int | None = None) -> None:
    """Set one or more library settings.
    All settings are thread-local.

    :param roll_size:
        Number of rolls in all simulations. Default: 100_000.
    """
    if roll_size is not None:
        _config.roll_size = roll_size
