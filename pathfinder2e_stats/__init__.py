import importlib.metadata

import pathfinder2e_stats.accessors  # noqa: F401
from pathfinder2e_stats.base import level2rank as level2rank
from pathfinder2e_stats.base import rank2level as rank2level
from pathfinder2e_stats.base import set_size as set_size
from pathfinder2e_stats.bonuses import sum_bonuses as sum_bonuses
from pathfinder2e_stats.check import DoS as DoS
from pathfinder2e_stats.check import check as check
from pathfinder2e_stats.check import map_outcome as map_outcome
from pathfinder2e_stats.damage import damage as damage
from pathfinder2e_stats.damage_spec import Damage as Damage
from pathfinder2e_stats.damage_spec import DamageList as DamageList
from pathfinder2e_stats.damage_spec import ExpandedDamage as ExpandedDamage
from pathfinder2e_stats.dice import d20 as d20
from pathfinder2e_stats.dice import roll as roll

try:
    __version__ = importlib.metadata.version("pathfinder2e_stats")
except importlib.metadata.PackageNotFoundError:  # pragma: nocover
    # Local copy, not installed with pip
    __version__ = "9999"
