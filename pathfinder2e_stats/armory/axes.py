from pathfinder2e_stats.armory._common import _weapon

__all__ = ("battle_axe", "dwarven_waraxe", "greataxe", "hatchet")

battle_axe = _weapon("battle_axe", "slashing", 8)
dwarven_waraxe = _weapon("dwarven_waraxe", "slashing", 8, two_hands=12)
greataxe = _weapon("greataxe", "slashing", 12)
hatchet = _weapon("hatchet", "slashing", 6)
