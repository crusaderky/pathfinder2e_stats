from __future__ import annotations

from pathfinder2e_stats.armory._common import _bleed_crit_weapon

__all__ = ("dagger", "flyssa", "kama", "kukri", "sickle")


dagger = _bleed_crit_weapon("dagger", "piercing", 4)
kama = _bleed_crit_weapon("kama", "slashing", 6)
kukri = _bleed_crit_weapon("kukri", "slashing", 6)
flyssa = _bleed_crit_weapon("flyssa", "piercing", 6)
sickle = _bleed_crit_weapon("sickle", "slashing", 4)
