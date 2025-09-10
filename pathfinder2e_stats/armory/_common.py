from collections.abc import Callable
from typing import Any

from pathfinder2e_stats.damage_spec import Damage


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
