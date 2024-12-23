from __future__ import annotations

from pathfinder2e_stats.armory._common import _bleed_crit_weapon

__all__ = ("arbalest", "crossbow", "hand_crossbow", "heavy_crossbow", "sukgung")


hand_crossbow = _bleed_crit_weapon("hand_crossbow", "piercing", 6)
crossbow = _bleed_crit_weapon("crossbow", "piercing", 8)
heavy_crossbow = _bleed_crit_weapon("heavy_crossbow", "piercing", 10)
arbalest = _bleed_crit_weapon("arbalest", "piercing", 10)
sukgung = _bleed_crit_weapon("sukgung", "piercing", 8, fatal_aim=12)
