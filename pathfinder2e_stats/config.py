from __future__ import annotations

import threading
from collections.abc import Collection, Hashable
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
    #: Default `independent_dims` parameter for :func:`~pathfinder2e_stats.check`.
    check_independent_dims: set[Hashable]
    #: Default `dependent_dims` parameter for :func:`~pathfinder2e_stats.check`.
    check_dependent_dims: set[Hashable]
    #: Default `independent_dims` parameter for :func:`~pathfinder2e_stats.damage`.
    damage_independent_dims: set[Hashable]
    #: Default `dependent_dims` parameter for :func:`~pathfinder2e_stats.damage`.
    damage_dependent_dims: set[Hashable]


def get_config() -> Config:
    """Return the current configuration settings."""
    d = _config.__dict__.copy()
    d.pop("rng", None)
    d.setdefault("roll_size", _roll_size_default)
    d.setdefault("check_independent_dims", set())
    d.setdefault("check_dependent_dims", set())
    d.setdefault("damage_independent_dims", set())
    d.setdefault("damage_dependent_dims", set())
    return cast(Config, d)


def set_config(
    roll_size: int | None = None,
    check_independent_dims: Collection[Hashable] | None = None,
    check_dependent_dims: Collection[Hashable] | None = None,
    damage_independent_dims: Collection[Hashable] | None = None,
    damage_dependent_dims: Collection[Hashable] | None = None,
) -> None:
    """Set one or more library settings.
    All settings are thread-local.

    :param roll_size:
        Number of rolls in all simulations. Default: 100_000.
    :param check_independent_dims:
        Default `independent_dims` parameter for :func:`check`.

        If the `independent_dims` parameter is explicitly specified
        in the function call, the parameter items adds to this set.
        If the `dependent_dims` parameter is explicitly specified
        in the function call, the parameter items detract from this set.

        You may also add/remove single elements with:

        >>> get_config()["check_independent_dims"].add("my_dim")

        Default: empty set (but `roll` is always independent).

    :param check_dependent_dims:
        Default `dependent_dims` parameter for :func:`check`.

        If the `dependent_dims` parameter is explicitly specified
        in the function call, the parameter items adds to this set.
        If the `independent_dims` parameter is explicitly specified
        in the function call, the parameter items detract from this set.

        You may also add/remove single elements with:

        >>> get_config()["check_dependent_dims"].add("my_dim")

        Default: empty set.

    :param damage_independent_dims:
        Default `independent_dims` parameter for :func:`damage`.
        All notes for `check_independent_dims` apply.

        Default: empty set (but `roll` and `damage_type` are always independent).

    :param damage_dependent_dims:
        Default `dependent_dims` parameter for :func:`damage`.
        All notes for `check_dependent_dims` apply.

        Default: empty set.

    .. only:: doctest

        >>> set_config(check_independent_dims=(), check_dependent_dims=())
    """
    if roll_size is not None:
        _config.roll_size = roll_size
    if check_independent_dims is not None:
        _config.check_independent_dims = set(check_independent_dims)
    if check_dependent_dims is not None:
        _config.check_dependent_dims = set(check_dependent_dims)
    if damage_independent_dims is not None:
        _config.damage_independent_dims = set(damage_independent_dims)
    if damage_dependent_dims is not None:
        _config.damage_dependent_dims = set(damage_dependent_dims)
