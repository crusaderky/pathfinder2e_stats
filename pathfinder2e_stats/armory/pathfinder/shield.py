from pathfinder2e_stats.armory._common import _weapon

__all__ = ("shield_bash", "shield_boss", "shield_spikes")

shield_bash = _weapon("shield bash", "bludgeoning", 4)
shield_boss = _weapon("shield boss", "bludgeoning", 6)
shield_spikes = _weapon("shield spikes", "piercing", 6)
