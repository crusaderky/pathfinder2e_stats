from pathfinder2e_stats.armory._common import _weapon

__all__ = (
    "greatpick",
    "light_pick",
    "pick",
    "switchscythe",
    "tricky_pick",
)

light_pick = _weapon("light_pick", "piercing", 4, fatal=8)
pick = _weapon("pick", "piercing", 6, fatal=10)
greatpick = _weapon("greatpick", "piercing", 10, fatal=12)
switchscythe = _weapon("switchscythe", "piercing", 6, fatal=10)
tricky_pick = _weapon("tricky_pick", "piercing", 6, fatal=10)
