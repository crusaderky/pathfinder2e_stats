from pathfinder2e_stats.damage_spec import Damage


def sneak_attack(level: int = 1, *, dedication: bool = False) -> Damage:
    """Sneak Attack damage (:prd_classes:`Rogue <37>` class feature).

    For :prd_feats:`Sneak Attacker <5094>`, set `dedication` to True.
    """
    if dedication:
        return Damage("precision", 1, 6 if level >= 6 else 4)
    dice = (level + 7) // 6
    return Damage("precision", dice, 6)
