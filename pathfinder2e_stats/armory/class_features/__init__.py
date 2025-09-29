import warnings
from collections.abc import Callable

from pathfinder2e_stats.armory.class_features import (
    operative,
    rogue,
    swashbuckler,
)

__all__ = ("operative", "rogue", "swashbuckler")


def __dir__() -> tuple[str, ...]:
    return __all__


def __getattr__(name: str) -> Callable:
    """Deprecation cycle from 0.1.1 to 0.2.0"""

    for mod in (rogue, swashbuckler):
        if hasattr(mod, name):
            warnings.warn(
                f"pathfinder2e_stats.armory.class_features.{name} has been "
                f"moved to {mod.__name__}.{name}",
                FutureWarning,
                stacklevel=2,
            )
            return getattr(mod, name)

    raise AttributeError(f"module {__name__} has no attribute {name}")
