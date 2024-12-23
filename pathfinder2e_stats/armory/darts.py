from __future__ import annotations

from pathfinder2e_stats.armory._common import _bleed_crit_weapon

__all__ = ("dart", "javelin", "shuriken")


dart = _bleed_crit_weapon("dart", "piercing", 4)
javelin = _bleed_crit_weapon("javelin", "piercing", 6)
shuriken = _bleed_crit_weapon("shuriken", "piercing", 4)
