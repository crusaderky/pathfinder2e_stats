from pathfinder2e_stats.armory._common import _weapon

# Corrosive
acid_dart_rifle = _weapon("acid_dart_rifle", "acid", 8)
reality_ripper = _weapon("reality_ripper", "void", 8, deadly=10)

# Crossbow
crossbolter = _weapon("crossbolter", "piercing", 10, critical="crossbow")

# Cryo
zero_pistol = _weapon("zero_pistol", "cold", 6)
zero_cannon = _weapon("zero_cannon", "cold", 10)

# Dart
card_slinger = _weapon("card_slinger", "piercing", 4, deadly=8, critical="dart")
shuriken_drone = _weapon("shuriken_drone", "piercing", 4, critical="dart")

# Flame
flamethrower = _weapon("flamethrower", "fire", 10, critical="flame")

# Laser
aeon_rifle = _weapon("aeon_rifle", "fire", 10)
artillery_laser = _weapon("artillery_laser", "fire", 10, critical="flame")
laser_pistol = _weapon("laser_pistol", "fire", 6)
laser_rifle = _weapon("laser_rifle", "fire", 8)
rotolaser = _weapon("rotolaser", "fire", 8)

# Plasma
plasma_caster = _weapon("plasma_caster", "fire", 10, boost=10, critical="plasma")
plasma_cannon = _weapon("plasma_cannon", "fire", 12, critical="plasma")
starfall_pistol = _weapon("starfall_pistol", "fire", 6, critical="plasma")

# Projectile
autotarget_rifle = _weapon("autotarget_rifle", "piercing", 6)
breaching_gun = _weapon("breaching_gun", "piercing", 10, kickback=True)
gyrojet_pistol = _weapon("gyrojet_pistol", "piercing", 6)
machine_gun = _weapon("machine_gun", "piercing", 8)
magnetar_rifle = _weapon("magnetar_rifle", "piercing", 12)
reaction_breacher = _weapon("reaction_breacher", "piercing", 8)
rotating_pistol = _weapon("rotating_pistol", "piercing", 6)
scattergun = _weapon("scattergun", "piercing", 8)
semi_auto_pistol = _weapon("semi_auto_pistol", "piercing", 6)
stellar_cannon = _weapon("stellar_cannon", "piercing", 10)

# Shock
arc_emitter = _weapon("arc_emitter", "electricity", 8)
arc_pistol = _weapon("arc_pistol", "electricity", 4)
arc_rifle = _weapon("arc_rifle", "electricity", 6)
pulsecaster_pistol = _weapon("pulsecaster_pistol", "electricity", 6)
singing_coil = _weapon("singing_coil", "electricity", 8)

# Sniper
assassin_rifle = _weapon(
    "assassin_rifle", "piercing", 10, fatal=12, kickback=True, critical="sniper"
)
coil_rifle = _weapon(
    "coil_rifle", "piercing", 10, boost=10, kickback=True, critical="sniper"
)
seeker_rifle = _weapon("seeker_rifle", "piercing", 10, kickback=True, critical="sniper")
shirren_eye_rifle = _weapon(
    "shirren_eye_rifle", "piercing", 10, deadly=12, kickback=True, critical="sniper"
)
shobhad_longrifle = _weapon(
    "shobhad_longrifle", "piercing", 8, fatal=12, kickback=True, critical="sniper"
)

# Sonic
boom_pistol = _weapon("boom_pistol", "sonic", 6, boost=8)
screamer = _weapon("screamer", "sonic", 12)
sonic_rifle = _weapon("sonic_rifle", "sonic", 6, boost=8)
streetsweeper = _weapon("streetsweeper", "sonic", 10, boost=10)
