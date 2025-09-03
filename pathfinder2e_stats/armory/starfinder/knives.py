from pathfinder2e_stats.armory._common import _critical_persistent_damage, _weapon

__all__ = ("aucturnite_chakram", "critical_specialization", "knife")

aucturnite_chakram = _weapon("aucturnite_chakram", "slashing", 6)
knife = _weapon("knife", "piercing", 4)
critical_specialization = _critical_persistent_damage("bleed", 6)
