from __future__ import annotations

from pathfinder2e_stats.armory._common import _weapon

__all__ = (
    "earthbreaker",
    "gnome_hooked_hammer",
    "light_hammer",
    "long_hammer",
    "maul",
    "warhammer",
)

earthbreaker = _weapon("earthbreaker", "bludgeoning", 6, two_hands=10)
gnome_hooked_hammer = _weapon("gnome_hooked_hammer", "bludgeoning", 6, two_hands=10)
light_hammer = _weapon("light_hammer", "bludgeoning", 6)
long_hammer = _weapon("long_hammer", "bludgeoning", 8)
maul = _weapon("maul", "bludgeoning", 12)
warhammer = _weapon("warhammer", "bludgeoning", 8)
