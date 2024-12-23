from __future__ import annotations

from typing import Literal

from pathfinder2e_stats.armory._common import _bleed_crit_weapon
from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("arbalest", "crossbow", "hand_crossbow", "heavy_crossbow", "sukgung")


hand_crossbow = _bleed_crit_weapon("hand_crossbow", "piercing", 6)
crossbow = _bleed_crit_weapon("crossbow", "piercing", 8)
heavy_crossbow = _bleed_crit_weapon("heavy_crossbow", "piercing", 10)
arbalest = _bleed_crit_weapon("arbalest", "piercing", 10)


def sukgung(
    dice: int = 1,
    bonus: int = 0,
    critical_specialization: bool = False,
    item_attack_bonus: int = 1,
    hands: Literal[1, 2, None] = None,
) -> Damage | ExpandedDamage:
    spec = Damage("piercing", dice, 8, bonus, fatal_aim=12)
    if hands is not None:
        spec = spec.hands(hands)
    if not critical_specialization:
        return spec
    bleed = Damage("bleed", 1, 6, item_attack_bonus, persistent=True)
    return spec.expand() + {DoS.critical_success: [bleed]}
