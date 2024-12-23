from __future__ import annotations

from pathfinder2e_stats.damage_spec import Damage

__all__ = ("longbow", "shortbow")


def shortbow(dice: int = 1, bonus: int = 0) -> Damage:
    """Shortbow and composite shortbow"""
    return Damage("piercing", dice, 6, bonus, deadly=8)


def longbow(dice: int = 1, bonus: int = 0) -> Damage:
    """Longbow and composite longbow"""
    return Damage("piercing", dice, 8, bonus, deadly=10)
