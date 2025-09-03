from pathfinder2e_stats.armory._common import _weapon

__all__ = ("longbow", "shortbow")

longbow = _weapon("longbow", "piercing", 8, deadly=10)
shortbow = _weapon("shortbow", "piercing", 6, deadly=8)
