from collections.abc import Callable

from pathfinder2e_stats.damage_spec import Damage, DoS, ExpandedDamage


def _critical_persistent_damage(
    type: str, faces: int
) -> Callable[[int], ExpandedDamage]:
    def critical_specialization(item_attack_bonus: int) -> ExpandedDamage:
        base = Damage(type, 1, faces, item_attack_bonus, persistent=True)
        return ExpandedDamage({DoS.critical_success: [base]})

    critical_specialization.__doc__ = f"""
    Critical specialization effect, to be added to the base weapon damage.

    The target takes 1d{faces} persistent {type} damage. You gain an item bonus to this
    {type} damage equal to the weapon's item bonus to attack rolls.
    """

    return critical_specialization


crossbow = _critical_persistent_damage("bleed", 8)
knife = _critical_persistent_damage("bleed", 6)
flame = _critical_persistent_damage("fire", 6)
plasma = _critical_persistent_damage("electricity", 6)


def dart(item_attack_bonus: int, *, grievous: bool = False) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 1d6 persistent bleed damage. You gain an item bonus to this
    bleed damage equal to the weapon's item bonus to attack rolls.

    :prd_equipment:`Grievous <2841>` rune:
    The base persistent bleed damage increases to 2d6.
    """
    bleed = Damage("bleed", 2 if grievous else 1, 6, item_attack_bonus, persistent=True)
    return ExpandedDamage({DoS.critical_success: [bleed]})


def pick(
    dice: int, *, grievous: bool = False, type: str = "piercing"
) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The weapon viciously pierces the target, who takes 2 additional damage per weapon
    damage die.

    :prd_equipment:`Grievous <2841>` rune:
    The extra damage from the critical specialization effect increases to 4 per
    weapon damage die.
    """
    bonus = dice * (4 if grievous else 2)
    return ExpandedDamage({DoS.critical_success: [Damage(type, 0, 0, bonus)]})


def sniper(dice: int, type: str = "piercing") -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 2 additional damage per weapon damage die.
    """
    bonus = dice * 2
    return ExpandedDamage({DoS.critical_success: [Damage(type, 0, 0, bonus)]})
