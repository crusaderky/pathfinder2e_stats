from types import ModuleType

from pathfinder2e_stats.armory import (
    _common,
    cantrips,
    class_features,
    critical_specialization,
    pathfinder,
    runes,
    spells,
    starfinder,
)

__all__ = (
    "cantrips",
    "class_features",
    "critical_specialization",
    "pathfinder",
    "runes",
    "spells",
    "starfinder",
)


def __dir__() -> tuple[str, ...]:
    return __all__


def _build_docstrings_for_mod(mod: ModuleType, tag: str) -> None:
    for name in mod.__all__:
        func = getattr(mod, name)

        item_name = name.replace("_", " ").title()
        msg = f"{tag}`{item_name}`\n\n{func()}"

        if not func.__doc__:
            func.__doc__ = msg
        else:
            func.__doc__ = msg + "\n\n" + func.__doc__.strip()


def _build_docstrings() -> None:
    for mod in globals().values():
        if isinstance(mod, ModuleType) and mod not in {
            _common,
            critical_specialization,
            pathfinder,
            starfinder,
        }:
            _build_docstrings_for_mod(mod, ":prd:")
    for mod in pathfinder.__dict__.values():
        if isinstance(mod, ModuleType):
            _build_docstrings_for_mod(mod, ":prd:")
    for mod in starfinder.__dict__.values():
        if isinstance(mod, ModuleType):
            _build_docstrings_for_mod(mod, ":srd:")


_build_docstrings()
