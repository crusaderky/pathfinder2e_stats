import importlib.metadata

# Import implementation modules
from pathfinder2e_stats.base import set_size as set_size
from pathfinder2e_stats.dice import d20 as d20
from pathfinder2e_stats.dice import roll as roll

try:
    __version__ = importlib.metadata.version("pathfinder2e_stats")
except importlib.metadata.PackageNotFoundError:  # pragma: nocover
    # Local copy, not installed with pip
    __version__ = "9999"
