from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def entropic_destabilizer(level: int = 8) -> ExpandedDamage:
    dmg = Damage("void", 1, 4) + {
        DoS.critical_success: [
            Damage("void", 4 if level >= 15 else 2, 4, persistent=True)
        ]
    }
    assert isinstance(dmg, ExpandedDamage)
    return dmg


def loudener() -> Damage:
    return Damage("sonic", 1, 6)


def flaming(level: int = 8) -> ExpandedDamage:
    dmg = Damage("fire", 1, 6) + {
        DoS.critical_success: [
            Damage("fire", 2 if level >= 15 else 1, 10, persistent=True)
        ]
    }
    assert isinstance(dmg, ExpandedDamage)
    return dmg


def frost() -> Damage:
    return Damage("cold", 1, 6)


def shock(level: int = 8) -> Damage | ExpandedDamage:
    """
    .. note::

       Doesn't include damage dealt to secondary targets on a critical hit.

    .. note::
        Tactical Shock upgrades, unlike Greater Shock runes,
        deal extra damage on a critical hit.
    """
    if level >= 15:
        return ExpandedDamage(
            {
                DoS.critical_success: [Damage("electricity", 2, 10)],
                DoS.success: [Damage("electricity", 1, 6)],
            }
        )
    return Damage("electricity", 1, 6)
