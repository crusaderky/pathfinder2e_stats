from pathfinder2e_stats.armory._common import _weapon

__all__ = ("battleglove", "fist")

battleglove = _weapon("battleglove", "bludgeoning", 4)
fist = _weapon("fist", "bludgeoning", 4)
fist.__doc__ = "Basic unarmed strike; can be performed with any part of the body."
