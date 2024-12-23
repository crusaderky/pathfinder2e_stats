from __future__ import annotations

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("corrosive", "flaming", "frost", "shock", "vitalizing", "wounding")


def _no_double_on_crit(spec: Damage) -> ExpandedDamage:
    return ExpandedDamage({DoS.success: [spec], DoS.critical_success: [spec]})


def vitalizing(greater: bool = False) -> ExpandedDamage:
    """Vitalizing rune"""
    return _no_double_on_crit(
        Damage("vitality", 2 if greater else 1, 6, persistent=True)
    )


def wounding() -> Damage:
    """Wounding rune"""
    return Damage("bleed", 1, 6, persistent=True)


def flaming(greater: bool = False) -> ExpandedDamage:
    """Flaming rune"""
    return _no_double_on_crit(Damage("fire", 1, 6)) + {
        DoS.critical_success: [Damage("fire", 2 if greater else 1, 10, persistent=True)]
    }


def shock() -> ExpandedDamage:
    """Shock rune

    FIXME can't easily model damage dealt to secondary targets
    """
    return _no_double_on_crit(Damage("electricity", 1, 6))


def frost() -> ExpandedDamage:
    """Frost rune"""
    return _no_double_on_crit(Damage("cold", 1, 6))


def corrosive() -> ExpandedDamage:
    """Corrosive rune

    FIXME can't easily model damage dealt to secondary targets
    """
    return _no_double_on_crit(Damage("acid", 1, 6))
