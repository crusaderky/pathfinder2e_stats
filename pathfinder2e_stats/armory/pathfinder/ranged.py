from pathfinder2e_stats.armory._common import _weapon

# Bow
longbow = _weapon("longbow", "piercing", 8, deadly=10)
shortbow = _weapon("shortbow", "piercing", 6, deadly=8)

# Crossbow
arbalest = _weapon("arbalest", "piercing", 10, critical="crossbow")
crescent_cross = _weapon("crescent_cross", "piercing", 6, critical="crossbow")
crossbow = _weapon("crossbow", "piercing", 8, critical="crossbow")
gauntlet_bow = _weapon("gauntlet_bow", "piercing", 4, critical="crossbow")
hand_crossbow = _weapon("hand_crossbow", "piercing", 6, critical="crossbow")
heavy_crossbow = _weapon("heavy_crossbow", "piercing", 10, critical="crossbow")
sukgung = _weapon("sukgung", "piercing", 8, fatal_aim=12, critical="crossbow")

# Dart
dart = _weapon("dart", "piercing", 4, critical="dart")
javelin = _weapon("javelin", "piercing", 6, critical="dart")
shuriken = _weapon("shuriken", "piercing", 4, critical="dart")

# Knife
chakram = _weapon("chakram", "slashing", 8, critical="knife")
