import warnings

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def vitalizing(level: int = 6, *, greater: None = None) -> Damage:
    # Deprecated 'greater' parameter
    if isinstance(level, bool):  # positional
        greater = level  # type: ignore[assignment]
    if greater is not None:
        warnings.warn(  # type: ignore[unreachable]
            "The 'greater' parameter is deprecated; use 'level' instead.",
            FutureWarning,
            stacklevel=2,
        )
        if greater:
            level = 14

    dice = 2 if level >= 14 else 1
    return Damage("vitality", dice, 6, persistent=True)


def wounding() -> Damage:
    return Damage("bleed", 1, 6, persistent=True)


def corrosive() -> Damage:
    """
    .. note::

       Doesn't include damage dealt to armor on a critical hit
    """
    return Damage("acid", 1, 6)


def flaming(level: int = 8, *, greater: None = None) -> ExpandedDamage:
    # Deprecated 'greater' parameter
    if isinstance(level, bool):  # positional
        greater = level  # type: ignore[assignment]
    if greater is not None:
        warnings.warn(  # type: ignore[unreachable]
            "The 'greater' parameter is deprecated; use 'level' instead.",
            FutureWarning,
            stacklevel=2,
        )
        if greater:
            level = 15

    dice = 2 if level >= 15 else 1
    dmg = Damage("fire", 1, 6) + {
        DoS.critical_success: [Damage("fire", dice, 10, persistent=True)]
    }
    assert isinstance(dmg, ExpandedDamage)
    return dmg


def frost() -> Damage:
    return Damage("cold", 1, 6)


def shock() -> Damage:
    """
    .. note::

       Doesn't include damage dealt to secondary targets on a critical hit
    """
    return Damage("electricity", 1, 6)
