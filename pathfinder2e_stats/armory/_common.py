from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pathfinder2e_stats.damage_spec import Damage


def _weapon(name: str, type: str, faces: int, **kwargs: Any) -> Callable[..., Damage]:
    def f(dice: int = 1, bonus: int = 0) -> Damage:
        return Damage(type, dice, faces, bonus, **kwargs)

    f.__name__ = name
    return f
