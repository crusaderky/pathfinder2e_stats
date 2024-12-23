from __future__ import annotations

from types import ModuleType

from pathfinder2e_stats.armory import _common
from pathfinder2e_stats.armory import bows as bows
from pathfinder2e_stats.armory import cantrips as cantrips
from pathfinder2e_stats.armory import crossbows as crossbows
from pathfinder2e_stats.armory import darts as darts
from pathfinder2e_stats.armory import knives as knives
from pathfinder2e_stats.armory import picks as picks
from pathfinder2e_stats.armory import runes as runes
from pathfinder2e_stats.armory import spells as spells
from pathfinder2e_stats.armory import swords as swords


def _build_docstrings() -> None:
    for mod in globals().values():
        if isinstance(mod, ModuleType) and mod is not _common:
            for name in mod.__all__:
                func = getattr(mod, name)
                if not func.__doc__:
                    func.__doc__ = str(func())
                else:
                    func.__doc__ = str(func()) + "\n\n" + func.__doc__.strip()


_build_docstrings()
del _build_docstrings
