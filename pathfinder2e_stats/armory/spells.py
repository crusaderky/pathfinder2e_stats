from typing import Literal

from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, DamageList, ExpandedDamage


def biting_words(rank: int = 1) -> Damage:
    return Damage("sonic", rank * 2, 6)


def blazing_bolt(rank: int = 2, actions: Literal[1, 2, 3] = 3) -> Damage:
    dice = rank
    if actions > 1:
        dice *= 2
    return Damage("fire", dice, 6)


def blistering_invective(rank: int = 2) -> Damage:
    return Damage("fire", rank // 2 * 2, 6, persistent=True, basic_save=True)


def breathe_fire(rank: int = 1) -> Damage:
    return Damage("fire", rank * 2, 6, basic_save=True)


def brine_dragon_bile(rank: int = 2) -> Damage:
    return Damage("acid", rank // 2 * 2, 6, persistent=True)


def dehydrate(rank: int = 1) -> Damage:
    dice = (rank - 1) // 2 * 3 + 1
    return Damage("fire", dice, 6, basic_save=True, persistent=True)


def divine_wrath(rank: int = 4) -> ExpandedDamage:
    base = Damage("spirit", rank, 10)
    return ExpandedDamage(
        {
            DoS.success: [base.copy(multiplier=0.5)],
            DoS.failure: [base],
            DoS.critical_failure: [base],  # Doesn't double
        }
    )


def fireball(rank: int = 3) -> Damage:
    return Damage("fire", rank * 2, 6, basic_save=True)


def force_barrage(
    rank: int = 1,
    actions: Literal[1, 2, 3] = 3,
    corageous_anthem: bool = False,
) -> Damage:
    """
    .. note::

       This assumes that all force bolts are directed against a single target.
       Assumes no resistance.
    """
    bolts = (rank + 1) // 2 * actions
    return Damage("force", bolts, 4, bolts * (2 if corageous_anthem else 1))


def harm(rank: int = 1, harming_hands: bool = False) -> Damage:
    return Damage("void", rank, 10 if harming_hands else 8, basic_save=True)


def heal(rank: int = 1, healing_hands: bool = False) -> Damage:
    return Damage("vitality", rank, 10 if healing_hands else 8, basic_save=True)


def lightning_bolt(rank: int = 3) -> Damage:
    return Damage("electricity", rank + 1, 12, basic_save=True)


def organsight(rank: int = 3) -> Damage:
    return Damage("precision", rank + 1, 6)


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
