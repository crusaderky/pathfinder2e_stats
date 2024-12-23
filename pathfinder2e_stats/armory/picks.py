from __future__ import annotations

from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = (
    "critical_specialization",
    "greatpick",
    "light_pick",
    "pick",
    "switchscythe",
    "tricky_pick",
)


light_pick = _weapon("light_pick", "piercing", 4, fatal=8)
pick = _weapon("pick", "piercing", 6, fatal=10)
greatpick = _weapon("greatpick", "piercing", 10, fatal=12)
switchscythe = _weapon("switchscythe", "piercing", 6, fatal=10)
tricky_pick = _weapon("tricky_pick", "piercing", 6, fatal=10)


def critical_specialization(
    dice: int, *, grievous: bool = False, type: str = "piercing"
) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The weapon viciously pierces the target, who takes 2 additional damage per weapon
    damage die.

    **Grievious rune:** The extra damage from the critical specialization effect
    increases to 4 per weapon damage die.
    """
    bonus = dice * (4 if grievous else 2)
    return ExpandedDamage({DoS.critical_success: [Damage(type, 0, 0, bonus)]})
