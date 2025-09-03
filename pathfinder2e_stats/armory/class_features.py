from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, DamageList, ExpandedDamage

__all__ = (
    "bleeding_finisher",
    "confident_finisher",
    "finisher",
    "precise_finisher",
    "precise_strike",
    "sneak_attack",
)


def __dir__() -> tuple[str, ...]:
    return __all__


def sneak_attack(level: int = 1, dedication: bool = False) -> Damage:
    """Sneak Attack damage (:prd_classes:`Rogue <37>` class feature).

    For :prd_feats:`Sneak Attacker <5094>`, set `dedication` to True.
    """
    if dedication:
        return Damage("precision", 1, 6 if level >= 6 else 4)
    dice = (level + 7) // 6
    return Damage("precision", dice, 6)


def precise_strike(level: int = 1, dedication: bool = False) -> Damage:
    """Precise Strike damage (:prd_classes:`Swashbuckler <63>` class feature).
    This is the damage added to strikes that are not a Finisher.

    For :prd_feats:`Finishing Precision <6235>`, set `dedication` to True.
    """
    dice = 1 if dedication else (level + 7) // 4
    return Damage("precision", 0, 0, dice)


def finisher(level: int = 1, dedication: bool = False) -> Damage:
    """Base Finisher damage (:prd_classes:`Swashbuckler <63>` class feature).
    For :prd_feats:`Finishing Precision <6235>`, set `dedication` to True.
    """
    dice = 1 if dedication else (level + 7) // 4
    return Damage("precision", dice, 6)


def confident_finisher(level: int = 1) -> ExpandedDamage:
    f = finisher(level)
    return f + {DoS.failure: [f.copy(multiplier=0.5)]}


def precise_finisher(level: int = 6) -> ExpandedDamage:
    f = finisher(level)
    return f + {DoS.failure: [f]}


def bleeding_finisher(level: int = 8) -> DamageList:
    f = finisher(level)
    return f + f.copy(type="bleed", persistent=True)
