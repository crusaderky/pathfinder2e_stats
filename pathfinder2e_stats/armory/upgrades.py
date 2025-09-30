from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, DamageList, ExpandedDamage


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


def auto(level: int = 1) -> DamageList | ExpandedDamage:
    """Use all available weapon upgrades for energy damage.

    >>> auto(level=20)
    **Critical success** (1d6)x2 fire plus 2d10 electricity
    plus (1d6)x2 cold plus (1d6)x2 sonic plus 2d10 persistent fire
    **Success** 1d6 fire plus 1d6 electricity plus 1d6 cold plus 1d6 sonic
    """
    if level < 8:
        return DamageList()
    upgrades = flaming(level=level) + shock(level=level)
    if level >= 12:
        upgrades += frost()
    if level >= 19:
        upgrades += loudener()
    return upgrades


auto._setup_doc = False  # type: ignore[attr-defined]
