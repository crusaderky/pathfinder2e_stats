from __future__ import annotations

from collections.abc import Callable

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def _bleed_crit_weapon(
    name: str, type: str, faces: int
) -> Callable[..., Damage | ExpandedDamage]:
    def _weapon(
        dice: int = 1,
        bonus: int = 0,
        critical_specialization: bool = False,
        item_attack_bonus: int = 1,
    ) -> Damage | ExpandedDamage:
        spec = Damage(type, dice, faces, bonus)
        if not critical_specialization:
            return spec
        bleed = Damage("bleed", 1, 6, item_attack_bonus, persistent=True)
        return spec.expand() + {DoS.critical_success: [bleed]}

    _weapon.__name__ = name
    return _weapon
