from pathfinder2e_stats.check import DoS
from pathfinder2e_stats.damage_spec import Damage, ExpandedDamage

__all__ = ("critical_specialization",)


def __dir__() -> tuple[str, ...]:
    return __all__


def critical_specialization(dice: int, type: str = "piercing") -> ExpandedDamage:
    """Critical specialization effect, to be added to the base weapon damage.

    The target takes 2 additional damage per weapon damage die.
    """
    bonus = dice * 2
    return ExpandedDamage({DoS.critical_success: [Damage(type, 0, 0, bonus)]})
