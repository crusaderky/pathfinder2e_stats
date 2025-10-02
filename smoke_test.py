"""Test import the library and print essential information"""

import platform
import sys

import pathfinder2e_stats

print("Python interpreter:", sys.executable)
print("Python version    :", sys.version)
print("Platform          :", platform.platform())
print("Library path      :", pathfinder2e_stats.__file__)
print("Library version   :", pathfinder2e_stats.__version__)
