from __future__ import annotations

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("heavy_pick", "light_pick", "pick")


def _pick_specialization(
    spec: Damage, critical_specialization: bool, grievous: bool
) -> Damage | ExpandedDamage:
    if not critical_specialization:
        return spec
    bonus = spec.dice * (4 if grievous else 2)
    exp = spec + {DoS.critical_success: [Damage("piercing", 0, 0, bonus)]}
    assert isinstance(exp, ExpandedDamage)
    return exp


def light_pick(
    dice: int = 1,
    bonus: int = 0,
    critical_specialization: bool = False,
    grievous: bool = False,
) -> Damage | ExpandedDamage:
    spec = Damage("piercing", dice, 4, bonus, fatal=8)
    return _pick_specialization(spec, critical_specialization, grievous)


def pick(
    dice: int = 1,
    bonus: int = 0,
    critical_specialization: bool = False,
    grievous: bool = False,
) -> Damage | ExpandedDamage:
    spec = Damage("piercing", dice, 6, bonus, fatal=10)
    return _pick_specialization(spec, critical_specialization, grievous)


def heavy_pick(
    dice: int = 1,
    bonus: int = 0,
    critical_specialization: bool = False,
    grievous: bool = False,
) -> Damage | ExpandedDamage:
    spec = Damage("piercing", dice, 10, bonus, fatal=12)
    return _pick_specialization(spec, critical_specialization, grievous)
