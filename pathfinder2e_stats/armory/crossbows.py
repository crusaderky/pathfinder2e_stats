from __future__ import annotations

from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = (
    "arbalest",
    "crescent_cross",
    "critical_specialization",
    "crossbow",
    "gauntlet_bow",
    "hand_crossbow",
    "heavy_crossbow",
    "sukgung",
)


arbalest = _weapon("arbalest", "piercing", 10)
crescent_cross = _weapon("crescent_cross", "piercing", 6)
crossbow = _weapon("crossbow", "piercing", 8)
gauntlet_bow = _weapon("gauntlet_bow", "piercing", 4)
hand_crossbow = _weapon("hand_crossbow", "piercing", 6)
heavy_crossbow = _weapon("heavy_crossbow", "piercing", 10)
sukgung = _weapon("sukgung", "piercing", 8, fatal_aim=12)


def critical_specialization(item_attack_bonus: int) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 1d6 persistent bleed damage. You gain an item bonus to this
    bleed damage equal to the weapon's item bonus to attack rolls.
    """
    base = Damage("bleed", 1, 8, item_attack_bonus, persistent=True)
    return ExpandedDamage({DoS.critical_success: [base]})
