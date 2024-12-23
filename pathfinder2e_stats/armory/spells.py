from __future__ import annotations

from typing import Literal

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, DamageList, ExpandedDamage

__all__ = (
    "blazing_bolt",
    "breathe_fire",
    "brine_dragon_bile",
    "fireball",
    "force_barrage",
    "shocking_grasp",
    "thunderstrike",
)


def blazing_bolt(rank: int = 2, actions: Literal[1, 2, 3] = 3) -> Damage:
    dice = rank
    if actions > 1:
        dice *= 2
    return Damage("fire", dice, 6)


def brine_dragon_bile(rank: int = 2) -> Damage:
    return Damage("acid", 2 * (rank // 2), 6, persistent=True)


def breathe_fire(rank: int = 1) -> Damage:
    return Damage("fire", 2 * rank, 6, basic_save=True)


def fireball(rank: int = 3) -> Damage:
    return Damage("fire", 2 * rank, 6, basic_save=True)


def force_barrage(rank: int = 1, actions: Literal[1, 2, 3] = 3) -> Damage:
    """
    .. note::
       No attack roll or save!

       This assumes that all force bolts are directed against a single target.
       Assumes no resistance.
    """
    bolts = (rank + 1) // 2 * actions
    return Damage("force", bolts, 4, bolts)


def shocking_grasp(rank: int = 1, metal: bool = False) -> Damage | ExpandedDamage:
    d = Damage("electricity", rank + 1, 12)
    if not metal:
        return d
    p = Damage("electricity", 1, 4, rank - 1, persistent=True)
    return d.expand() + {DoS.critical_success: [p], DoS.success: [p]}


def thunderstrike(rank: int = 1) -> DamageList:
    e = Damage("electricity", rank, 12, basic_save=True)
    s = Damage("sonic", 1, 4, basic_save=True)
    return DamageList([e, s])
