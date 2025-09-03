from collections.abc import Callable
from typing import Any

from pathfinder2e_stats.damage_spec import Damage, DoS, ExpandedDamage


def _weapon(name: str, type: str, faces: int, **kwargs: Any) -> Callable[..., Damage]:
    def f(dice: int = 1, bonus: int = 0) -> Damage:
        return Damage(type, dice, faces, bonus, **kwargs)

    f.__name__ = name
    return f


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
