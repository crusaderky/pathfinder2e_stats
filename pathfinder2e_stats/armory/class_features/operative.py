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
