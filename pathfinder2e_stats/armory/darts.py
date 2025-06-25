from __future__ import annotations

from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("critical_specialization", "dart", "javelin", "shuriken")


dart = _weapon("dart", "piercing", 4)
javelin = _weapon("javelin", "piercing", 6)
shuriken = _weapon("shuriken", "piercing", 4)


def critical_specialization(
    item_attack_bonus: int, *, grievous: bool = False
) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 1d6 persistent bleed damage. You gain an item bonus to this
    bleed damage equal to the weapon's item bonus to attack rolls.

    :prd_equipment:`Grievous <2841>` rune:
    The base persistent bleed damage increases to 2d6.
    """
    bleed = Damage("bleed", 2 if grievous else 1, 6, item_attack_bonus, persistent=True)
    return ExpandedDamage({DoS.critical_success: [bleed]})
