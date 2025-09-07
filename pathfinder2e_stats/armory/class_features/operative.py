from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage


def aim(
    level: int = 1, *, devastating_aim: bool = False, dedication: bool = False
) -> Damage:
    """Aim damage (:srd_classes:`Operative <3-operative>` class feature).

    :param devastating_aim:
        :srd_feats:`Devastating Aim <536-devastating-aim>` feat
    :param dedication:
         Operative Archetype's :srd_feats:`Sharpshooter <718-sharpshooter>` feat
    """
    faces = 6 if devastating_aim else 4

    if dedication:
        return Damage("precision", 2 if level >= 6 else 1, faces)
    dice = (level + 7) // 6
    return Damage("precision", dice, faces)


def bloody_wounds(level: int = 1, *, dedication: bool = False) -> ExpandedDamage:
    """:srd_feats:`Bloody Wounds <535-bloody-wounds>` Operative feat.

    :param dedication:
         Operative Archetype's :srd_feats:`Sharpshooter <718-sharpshooter>` feat
    """
    aim_dice = aim(level, dedication=dedication).dice
    bleed = Damage("bleed", 0, 0, aim_dice, persistent=True)
    return ExpandedDamage({DoS.critical_success: [bleed]})


def critical_aim(critical_specialization: ExpandedDamage) -> ExpandedDamage:
    """Critical Aim (level 15 :srd_classes:`Operative <3-operative>` class feature).

    The first time in each round when you Aim and successfully make a ranged Strike
    against your mark, add your weapon's critical specialization effect to the attack
    even if you didn't score a critical hit.

    :param critical_specialization:
        The weapon's extra damage from critical specialization
    :returns:
        Additional damage on a hit. Note that this is in addition to the critical
        specialization damage and does not replace it.

    .. only:: doctest

        >>> from pathfinder2e_stats import armory

    **Example**

    >>> weapon = armory.starfinder.ranged.crossbolter(3, 4)  # 3d10+4
    >>> crit_spec = armory.critical_specialization.crossbow(2)  # 1d8+2 persistent bleed
    >>> crit_aim = armory.class_features.operative.critical_aim(crit_spec)
    >>> weapon + crit_spec + crit_aim  # First strike
    **Critical success** (3d10+4)x2 piercing plus 1d8+2 persistent bleed
    **Success** 3d10+4 piercing plus 1d8+2 persistent bleed
    >>> weapon + crit_spec  # Subsequent strikes
    **Critical success** (3d10+4)x2 piercing plus 1d8+2 persistent bleed
    **Success** 3d10+4 piercing
    """
    if not isinstance(critical_specialization, ExpandedDamage) or list(
        critical_specialization
    ) != [DoS.critical_success]:
        raise ValueError("argument does not look like a critical specialization effect")
    return ExpandedDamage({DoS.success: critical_specialization[DoS.critical_success]})


critical_aim._setup_doc = False  # type: ignore[attr-defined]
