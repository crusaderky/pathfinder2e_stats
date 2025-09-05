from pathfinder2e_stats.armory._common import _weapon

__all__ = ("doshko", "fangblade", "plasma_doshko")

doshko = _weapon("doshko", "piercing", 12)
fangblade = _weapon("fangblade", "slashing", 10, boost=12)
plasma_doshko = _weapon("plasma_doshko", "fire", 10, critical="plasma")
