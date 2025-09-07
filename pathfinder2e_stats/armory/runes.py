from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def vitalizing(greater: bool = False) -> Damage:
    return Damage("vitality", 2 if greater else 1, 6, persistent=True)


def wounding() -> Damage:
    return Damage("bleed", 1, 6, persistent=True)


def flaming(greater: bool = False) -> ExpandedDamage:
    dmg = Damage("fire", 1, 6) + {
        DoS.critical_success: [Damage("fire", 2 if greater else 1, 10, persistent=True)]
    }
    assert isinstance(dmg, ExpandedDamage)
    return dmg


def shock() -> Damage:
    """
    .. note::

       Doesn't include damage dealt to secondary targets on a critical hit
    """
    return Damage("electricity", 1, 6)


def frost() -> Damage:
    return Damage("cold", 1, 6)


def corrosive() -> Damage:
    """
    .. note::

       Doesn't include damage dealt to armor on a critical hit
    """
    return Damage("acid", 1, 6)
