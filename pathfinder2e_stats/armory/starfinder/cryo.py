from pathfinder2e_stats.armory._common import _weapon

__all__ = ("thermal_dynafan", "zero_knife")

thermal_dynafan = _weapon("thermal dynafan", "fire", 6, critical="flame")
zero_knife = _weapon("zero knife", "cold", 4)
