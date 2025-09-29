import warnings
from types import ModuleType
from typing import Literal

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


def _setup_mod(mod: ModuleType, tag: str | None) -> None:
    """Initialize __all__ and __dir__ for an armory module.

    Create or prepend to __doc__ the output of str(func()),
    i.e. the string representation of the Damage object
    returned by each function with its default parameters.
    """
    d = {
        name: func
        for name, func in mod.__dict__.items()
        if callable(func)
        and not name.startswith("_")
        and not isinstance(func, type)
        and func is not Literal
    }
    mod.__all__ = list(d)  # type: ignore[attr-defined]
    mod.__dir__ = lambda: list(d)  # type: ignore[method-assign]

    # critical_specialization functions always have mandatory parameters
    if mod is not critical_specialization:
        assert tag
        for name, func in d.items():
            if not getattr(func, "_setup_doc", True):
                continue

            item_name = name.replace("_", " ").title()
            msg = f"{tag}`{item_name}`\n\n{func()}"

            if not func.__doc__:
                func.__doc__ = msg
            else:
                func.__doc__ = msg + "\n\n" + func.__doc__.strip()


_setup_mod(class_features.operative, ":srd:")
_setup_mod(class_features.rogue, ":prd:")
_setup_mod(class_features.swashbuckler, ":prd:")
_setup_mod(pathfinder.melee, ":prd:")
_setup_mod(pathfinder.ranged, ":prd:")
_setup_mod(starfinder.melee, ":srd:")
_setup_mod(starfinder.ranged, ":srd:")
_setup_mod(critical_specialization, None)
_setup_mod(cantrips, ":prd:")
_setup_mod(runes, ":prd:")
_setup_mod(spells, ":prd:")


def __getattr__(name: str) -> ModuleType:
    """Deprecation cycle from 0.1.1 to 0.2.0"""

    if name not in (
        "axes",
        "bows",
        "crossbows",
        "darts",
        "hammers",
        "knives",
        "picks",
        "swords",
    ):
        raise AttributeError(f"module {__name__} has no attribute {name}")

    warnings.warn(
        f"pathfinder2e_stats.armory.{name} has been split into "
        "pathfinder2e_stats.armory.pathfinder.melee, "
        "pathfinder2e_stats.armory.pathfinder.ranged, and "
        "pathfinder2e_stats.armory.critical_specialization.",
        FutureWarning,
        stacklevel=2,
    )
    mod = ModuleType(name)
    mod.__dict__.update(pathfinder.melee.__dict__)
    mod.__dict__.update(pathfinder.ranged.__dict__)

    crit_spec = {
        "crossbows": critical_specialization.crossbow,
        "darts": critical_specialization.dart,
        "knives": critical_specialization.knife,
        "picks": critical_specialization.pick,
    }
    if name in crit_spec:
        mod.critical_specialization = crit_spec[name]  # type: ignore[attr-defined]

    return mod
