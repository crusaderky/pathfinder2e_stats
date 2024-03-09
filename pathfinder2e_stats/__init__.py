import importlib.metadata

from pathfinder2e_stats.base import DoS as DoS
from pathfinder2e_stats.base import set_size as set_size
from pathfinder2e_stats.check import check as check
from pathfinder2e_stats.check import map_outcomes as map_outcomes
from pathfinder2e_stats.damage_spec import Damage as Damage
from pathfinder2e_stats.damage_spec import ExpandedDamage as ExpandedDamage
from pathfinder2e_stats.dice import d20 as d20
from pathfinder2e_stats.dice import roll as roll

try:
    __version__ = importlib.metadata.version("pathfinder2e_stats")
except importlib.metadata.PackageNotFoundError:  # pragma: nocover
    # Local copy, not installed with pip
    __version__ = "9999"
