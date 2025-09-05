from pathfinder2e_stats.armory._common import _weapon

__all__ = (
    "bladed_gauntlet",
    "fangwire",
    "fist",
    "gauntlet",
    "knuckle_duster",
    "pantograph_gauntlet",
    "spiked_gauntlet",
    "tekko_kagi",
    "thorn_whip",
    "tonfa",
    "tri_bladed_katar",
)


bladed_gauntlet = _weapon("bladed_gauntlet", "slashing", 4)
fangwire = _weapon("fangwire", "slashing", 4, deadly=8)
fist = _weapon("fist", "bludgeoning", 4)
gauntlet = _weapon("gauntlet", "bludgeoning", 4)
knuckle_duster = _weapon("knuckle_duster", "bludgeoning", 4)
pantograph_gauntlet = _weapon("pantograph_gauntlet", "bludgeoning", 4, deadly=6)
spiked_gauntlet = _weapon("spiked_gauntlet", "piercing", 4)
tekko_kagi = _weapon("tekko_kagi", "slashing", 4)
thorn_whip = _weapon("thorn_whip", "piercing", 4)
tonfa = _weapon("tonfa", "bludgeoning", 4)
tri_bladed_katar = _weapon("tri_bladed_katar", "piercing", 4, fatal=8)

fist.__doc__ = """
Basic unarmed strike; can be performed with any part of the body.
For a :prd_classes:`Monk <60>`'s Powerful Fist, use

>>> fist().increase_die()
1d6 bludgeoning
"""
