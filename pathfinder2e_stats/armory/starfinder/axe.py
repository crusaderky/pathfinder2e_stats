from pathfinder2e_stats.armory._common import _weapon

__all__ = ("doshko", "fangblade", "plasma_doshko")

doshko = _weapon("doshko", "piercing", 12)
fangblade = _weapon("fangblade", "slashing", 10, boost=12)
plasma_doshko = _weapon("plasma_doshko", "fire", 10)

plasma_doshko.__doc__ = """
:func:`Critical (plasma)
<pathfinder2e_stats.armory.critical_specialization.plasma>`
"""
