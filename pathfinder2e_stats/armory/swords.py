from __future__ import annotations

from pathfinder2e_stats.damage_spec import Damage

__all__ = ("bastard_sword", "greatsword", "longsword", "rapier", "shortsword")


def shortsword(dice: int = 1, bonus: int = 0) -> Damage:
    return Damage("slashing", dice, 6, bonus)


def rapier(dice: int = 1, bonus: int = 0) -> Damage:
    return Damage("slashing", dice, 6, bonus, deadly=8)


def longsword(dice: int = 1, bonus: int = 0) -> Damage:
    return Damage("slashing", dice, 8, bonus)


def bastard_sword(dice: int = 1, bonus: int = 0) -> Damage:
    return Damage("slashing", dice, 8, bonus, two_hands=12)


def greatsword(dice: int = 1, bonus: int = 0) -> Damage:
    return Damage("slashing", dice, 12, bonus)
