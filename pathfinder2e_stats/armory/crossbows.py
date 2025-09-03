from pathfinder2e_stats.armory._common import _critical_persistent_damage, _weapon

__all__ = (
    "arbalest",
    "crescent_cross",
    "critical_specialization",
    "crossbow",
    "gauntlet_bow",
    "hand_crossbow",
    "heavy_crossbow",
    "sukgung",
)


arbalest = _weapon("arbalest", "piercing", 10)
crescent_cross = _weapon("crescent_cross", "piercing", 6)
crossbow = _weapon("crossbow", "piercing", 8)
gauntlet_bow = _weapon("gauntlet_bow", "piercing", 4)
hand_crossbow = _weapon("hand_crossbow", "piercing", 6)
heavy_crossbow = _weapon("heavy_crossbow", "piercing", 10)
sukgung = _weapon("sukgung", "piercing", 8, fatal_aim=12)
critical_specialization = _critical_persistent_damage("bleed", 8)
