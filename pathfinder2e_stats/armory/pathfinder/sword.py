from pathfinder2e_stats.armory._common import _weapon

__all__ = ("bastard_sword", "greatsword", "longsword", "rapier", "shortsword")

shortsword = _weapon("shortsword", "slashing", 6)
rapier = _weapon("rapier", "piercing", 6, deadly=8)
longsword = _weapon("longsword", "slashing", 8)
bastard_sword = _weapon("bastard_sword", "slashing", 8, two_hands=12)
greatsword = _weapon("greatsword", "slashing", 12)
