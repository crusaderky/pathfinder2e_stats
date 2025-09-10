from collections.abc import Callable
from typing import Any

from pathfinder2e_stats.damage_spec import Damage, DamageList


def _weapon(
    name: str,
    type: str,
    faces: int,
    *,
    critical: str | None = None,
    kickback: bool = False,
    **kwargs: Any,
) -> Callable[..., Damage]:
    def f(dice: int = 1, bonus: int = 0) -> Damage:
        return Damage(type, dice, faces, bonus + int(kickback), **kwargs)

    f.__name__ = name
    if critical:
        f.__doc__ = (
            f":func:`Critical ({critical}) "
            f"<pathfinder2e_stats.armory.critical_specialization.{critical}>`"
        )
    return f


def _scatter_weapon(
    name: str,
    type: str,
    faces: int,
    *,
    kickback: bool = False,
    **kwargs: Any,
) -> Callable[..., DamageList]:
    """Generate a weapon with the scatter trait."""

    def f(dice: int = 1, bonus: int = 0) -> DamageList:
        """:prd_traits:`Scatter <848>`:
        This weapon fires a cluster of pellets in a wide spray. Scatter always has an
        area listed with it, indicating the radius of the spray. On a hit, the primary
        target of attacks with a scatter weapon take the listed damage, and the target
        and all other creatures within the listed radius around it take 1 point of
        splash damage per weapon damage die, of the same type as the initial attack.
        """
        return DamageList(
            [
                Damage(type, dice, faces, bonus + int(kickback), **kwargs),
                Damage(type, 0, 0, dice, splash=True),
            ]
        )

    f.__name__ = name
    return f
