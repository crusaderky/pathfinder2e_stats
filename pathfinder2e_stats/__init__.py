import importlib.metadata

# Import implementation modules
from pathfinder2e_stats.helloworld import hello

try:
    __version__ = importlib.metadata.version("pathfinder2e_stats")
except importlib.metadata.PackageNotFoundError:  # pragma: nocover
    # Local copy, not installed with pip
    __version__ = "999"


__all__ = ("__version__", "hello")
