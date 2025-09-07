from types import ModuleType

from pathfinder2e_stats.armory import (
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
        if not callable(func):
            continue

        item_name = name.replace("_", " ").title()
        msg = f"{tag}`{item_name}`\n\n{func()}"

        if not func.__doc__:
            func.__doc__ = msg
        else:
            func.__doc__ = msg + "\n\n" + func.__doc__.strip()


def _build_docstrings() -> None:
    for mod in pathfinder.__dict__.values():
        if isinstance(mod, ModuleType):
            _build_docstrings_for_mod(mod, ":prd:")
    for mod in starfinder.__dict__.values():
        if isinstance(mod, ModuleType):
            _build_docstrings_for_mod(mod, ":srd:")

    _build_docstrings_for_mod(cantrips, ":prd:")
    _build_docstrings_for_mod(class_features.operative, ":srd:")
    _build_docstrings_for_mod(class_features.rogue, ":prd:")
    _build_docstrings_for_mod(class_features.swashbuckler, ":prd:")
    _build_docstrings_for_mod(runes, ":prd:")
    _build_docstrings_for_mod(spells, ":prd:")


_build_docstrings()
