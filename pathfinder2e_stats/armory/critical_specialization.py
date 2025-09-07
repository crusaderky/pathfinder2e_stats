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


def axe(weapon: Damage) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    Choose one creature adjacent to the initial target and within reach. If its AC is
    lower than your attack roll result for the critical hit, you deal damage to that
    creature equal to the result of the weapon damage die you rolled (including extra
    dice for its striking rune, if any). This amount isn't doubled, and no bonuses or
    other additional dice apply to this damage.

    .. note::
        This damage should not be added to the base weapon damage, as it applies to
        a different target.

    :param weapon:
        The base weapon damage, including any extra dice from a striking rune, strength,
        etc. but excluding property runes.
    :returns:
        Damage dealt to the secondary target.

    **Example**

    .. only:: doctest

        >>> from pathfinder2e_stats import armory, check, damage, seed
        >>> seed(0)

    >>> base_axe = armory.pathfinder.melee.greataxe(2, 6)  # 2d12+6
    >>> axe_crit = armory.critical_specialization.axe(base_axe)
    >>> axe_crit
    **Critical success** 2d12 slashing

    Property runes, if any, must be added afterwards:

    >>> axe = base_axe + armory.runes.flaming()
    >>> primary_attack = check(15, DC=23)

    Damage to primary target, on hit and critical hit:

    >>> primary_damage = damage(primary_attack, axe)

    Damage to second target from critical specialization effect:
    2~24 damage when primary target is critically hit.
    Note: simplified use case where the secondary target has the same
    or lower AC as the primary target.

    >>> secondary_damage = damage(primary_attack, axe_crit)
    """
    if not isinstance(weapon, Damage):
        raise ValueError(
            "argument damage must not include property runes, precision damage, etc."
        )
    # Warn if the user did not explicitly call hands() for two-hands weapons
    weapon = weapon._auto_optionals()
    base = Damage(weapon.type, weapon.dice, weapon.faces)
    return ExpandedDamage({DoS.critical_success: [base]})


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
