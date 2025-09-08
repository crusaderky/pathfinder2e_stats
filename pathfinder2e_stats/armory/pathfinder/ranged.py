from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.damage_spec import Damage

# Bow
daikyu = _weapon("daikyu", "piercing", 8)
gakgung = _weapon("gakgung", "piercing", 6, deadly=8)
hongali_hornbow = _weapon("hongali_hornbow", "piercing", 8, deadly=6)
longbow = _weapon("longbow", "piercing", 8, deadly=10)
mikazuki = _weapon("mikazuki", "piercing", 6)
shortbow = _weapon("shortbow", "piercing", 6, deadly=8)
phalanx_piercer = _weapon("phalanx_piercer", "piercing", 10)
shield_bow = _weapon("shield_bow", "piercing", 8, deadly=8)

# Club
boomerang = _weapon("boomerang", "bludgeoning", 6)

# Crossbow
arbalest = _weapon("arbalest", "piercing", 10, critical="crossbow")
backpack_ballista = _weapon("backpack_ballista", "piercing", 12, critical="crossbow")
crescent_cross = _weapon("crescent_cross", "piercing", 6, critical="crossbow")
crossbow = _weapon("crossbow", "piercing", 8, critical="crossbow")
gauntlet_bow = _weapon("gauntlet_bow", "piercing", 4, critical="crossbow")
hand_crossbow = _weapon("hand_crossbow", "piercing", 6, critical="crossbow")
heavy_crossbow = _weapon("heavy_crossbow", "piercing", 10, critical="crossbow")
lancer = _weapon("lancer", "piercing", 8, critical="crossbow")
repeating_crossbow = _weapon("repeating_crossbow", "piercing", 8, critical="crossbow")
repeating_hand_crossbow = _weapon(
    "repeating_hand_crossbow", "piercing", 8, critical="crossbow"
)
repeating_heavy_crossbow = _weapon(
    "repeating_heavy_crossbow", "piercing", 10, critical="crossbow"
)
rotary_bow = _weapon("rotary_bow", "piercing", 8, critical="crossbow")
sukgung = _weapon("sukgung", "piercing", 8, fatal_aim=12, critical="crossbow")
taw_launcher = _weapon("taw_launcher", "piercing", 10, deadly=10, critical="crossbow")

# Dart
atlatl = _weapon("atlatl", "piercing", 6, critical="dart")
chakri = _weapon("chakri", "slashing", 6, critical="dart")
dart = _weapon("dart", "piercing", 4, critical="dart")
harpoon = _weapon("harpoon", "piercing", 8, critical="dart")
javelin = _weapon("javelin", "piercing", 6, critical="dart")
shuriken = _weapon("shuriken", "piercing", 4, critical="dart")
wrist_launcher = _weapon("wrist_launcher", "piercing", 4, critical="dart")


def blowgun(dice: int = 0, bonus: int = 0) -> Damage:  # noqa: ARG001
    """:func:`Critical (dart) <pathfinder2e_stats.armory.critical_specialization.dart>`

    .. note::
       This weapon has no weapon dice.
    """
    return Damage("piercing", 0, 0, bonus + 1)


def dart_umbrella(dice: int = 0, bonus: int = 0) -> Damage:  # noqa: ARG001
    """:func:`Critical (dart) <pathfinder2e_stats.armory.critical_specialization.dart>`

    .. note::
       This weapon has no weapon dice.
    """
    return Damage("piercing", 0, 0, bonus + 1)


# Firearm
# TODO missing entries

# Knife
chakram = _weapon("chakram", "slashing", 8, critical="knife")
