from pathfinder2e_stats.armory.starfinder import (
    clubs,
    crossbows,
    darts,
    flame,
    knives,
    plasma,
    snipers,
    swords,
)

__all__ = (
    "clubs",
    "crossbows",
    "darts",
    "flame",
    "knives",
    "plasma",
    "snipers",
    "swords",
)


def __dir__() -> tuple[str, ...]:
    return __all__
