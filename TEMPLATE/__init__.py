import importlib.metadata

# Import implementation modules
from TEMPLATE.helloworld import hello

try:
    __version__ = importlib.metadata.version("TEMPLATE")
except importlib.metadata.PackageNotFoundError:  # pragma: nocover
    # Local copy, not installed with pip
    __version__ = "999"


__all__ = ("__version__", "hello")
