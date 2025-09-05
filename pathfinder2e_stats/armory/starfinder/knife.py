from pathfinder2e_stats.armory._common import _weapon

__all__ = ("aucturnite_chakram", "knife", "shooting_starknife", "tailblade", "talon")

aucturnite_chakram = _weapon("aucturnite_chakram", "slashing", 6)
knife = _weapon("knife", "piercing", 4)
shooting_starknife = _weapon("shooting_starknife", "piercing", 4, deadly=6)
tailblade = _weapon("tailblade", "slashing", 4)
talon = _weapon("talon", "acid", 6)
