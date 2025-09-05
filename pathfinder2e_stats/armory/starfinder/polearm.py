from pathfinder2e_stats.armory._common import _weapon

__all__ = ("cryopike", "painglaive")

cryopike = _weapon("cryopike", "cold", 10)
painglaive = _weapon("painglaive", "slashing", 10, boost=10)
