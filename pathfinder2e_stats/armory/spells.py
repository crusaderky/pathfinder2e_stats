from __future__ import annotations

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import AnyDamageSpec, Damage

__all__ = (
    "breathe_fire",
    "brine_dragon_bile",
    "fireball",
    "shocking_grasp",
    "thunderstrike",
)


def brine_dragon_bile(rank: int = 2) -> Damage:
    return Damage("acid", 2 * (rank // 2), 6, persistent=True)


def breathe_fire(rank: int = 1) -> Damage:
    return Damage("fire", 2 * rank, 6, basic_save=True)


def fireball(rank: int = 3) -> Damage:
    return Damage("fire", 2 * rank, 6, basic_save=True)


def shocking_grasp(rank: int = 1, metal: bool = False) -> AnyDamageSpec:
    d = Damage("electricity", rank + 1, 12)
    if not metal:
        return d
    p = Damage("electricity", 1, 4, rank - 1, persistent=True)
    return d + {DoS.critical_success: [p], DoS.success: [p]}


def thunderstrike(rank: int = 1) -> AnyDamageSpec:
    e = Damage("electricity", rank, 12, basic_save=True)
    s = Damage("sonic", 1, 4, basic_save=True)
    return e + s
