from pathfinder2e_stats.armory._common import _critical_persistent_damage, _weapon

__all__ = ("critical_specialization", "dagger", "flyssa", "kama", "kukri", "sickle")


dagger = _weapon("dagger", "piercing", 4)
kama = _weapon("kama", "slashing", 6)
kukri = _weapon("kukri", "slashing", 6)
flyssa = _weapon("flyssa", "piercing", 6)
sickle = _weapon("sickle", "slashing", 4)
critical_specialization = _critical_persistent_damage("bleed", 6)
