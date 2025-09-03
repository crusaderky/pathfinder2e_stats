from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("critical_specialization", "dagger", "flyssa", "kama", "kukri", "sickle")


def __dir__() -> tuple[str, ...]:
    return __all__


dagger = _weapon("dagger", "piercing", 4)
kama = _weapon("kama", "slashing", 6)
kukri = _weapon("kukri", "slashing", 6)
flyssa = _weapon("flyssa", "piercing", 6)
sickle = _weapon("sickle", "slashing", 4)


def critical_specialization(item_attack_bonus: int) -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 1d6 persistent bleed damage. You gain an item bonus to this
    bleed damage equal to the weapon's item bonus to attack rolls.
    """
    bleed = Damage("bleed", 1, 6, item_attack_bonus, persistent=True)
    return ExpandedDamage({DoS.critical_success: [bleed]})
