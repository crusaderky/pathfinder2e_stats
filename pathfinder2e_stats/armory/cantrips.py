from __future__ import annotations

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import AnyDamageSpec, Damage

__all__ = ("electric_arc", "frostbite", "ignition", "live_wire", "ray_of_frost")


def ignition(rank: int = 1, melee: bool = False) -> AnyDamageSpec:
    base = Damage("fire", rank + 1, 6 if melee else 4)
    return base + {DoS.critical_success: [base.copy(persistent=True)]}


def live_wire(rank: int = 1) -> AnyDamageSpec:
    dice = (rank + 1) // 2
    return (
        Damage("slashing", dice, 4)
        + Damage("electricity", dice, 4)
        + {
            DoS.critical_success: [Damage("electricity", dice, 4, persistent=True)],
            DoS.failure: [Damage("electricity", dice, 4)],
        }
    )


def electric_arc(rank: int = 1) -> Damage:
    return Damage("electricity", rank + 1, 4, basic_save=True)


def ray_of_frost(rank: int = 1) -> Damage:
    return Damage("cold", rank + 1, 4)


def frostbite(rank: int = 1) -> Damage:
    return Damage("cold", rank + 1, 4, basic_save=True)
