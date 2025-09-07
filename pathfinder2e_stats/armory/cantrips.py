from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def daze(rank: int = 1) -> Damage:
    dice = (rank + 1) // 2
    return Damage("mental", dice, 6, basic_save=True)


def electric_arc(rank: int = 1) -> Damage:
    return Damage("electricity", rank + 1, 4, basic_save=True)


def frostbite(rank: int = 1) -> Damage:
    return Damage("cold", rank + 1, 4, basic_save=True)


def haunting_hymn(rank: int = 1) -> Damage:
    dice = (rank + 1) // 2
    return Damage("sonic", dice, 8, basic_save=True)


def ignition(rank: int = 1, melee: bool = False) -> ExpandedDamage:
    base = Damage("fire", rank + 1, 6 if melee else 4)
    return base.expand() + {DoS.critical_success: [base.copy(persistent=True)]}


def live_wire(rank: int = 1) -> ExpandedDamage:
    dice = (rank + 1) // 2
    return (
        Damage("slashing", dice, 4).expand()
        + Damage("electricity", dice, 4)
        + {
            DoS.critical_success: [Damage("electricity", dice, 4, persistent=True)],
            DoS.failure: [Damage("electricity", dice, 4)],
        }
    )


def needle_darts(rank: int = 1) -> ExpandedDamage:
    return Damage("piercing", rank + 2, 4) + {
        DoS.critical_success: [Damage("bleed", 0, 0, rank, persistent=True)]
    }


def ray_of_frost(rank: int = 1) -> Damage:
    return Damage("cold", rank + 1, 4)


def void_warp(rank: int = 1) -> Damage:
    return Damage("void", rank + 1, 4, basic_save=True)
