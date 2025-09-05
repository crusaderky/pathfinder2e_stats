from pathfinder2e_stats.armory._common import _weapon

__all__ = ("baton", "bone_scepter", "shock_truncheon")

baton = _weapon("baton", "bludgeoning", 6)
bone_scepter = _weapon("bone_scepter", "cold", 6)
shock_truncheon = _weapon("shock_truncheon", "electricity", 6)
