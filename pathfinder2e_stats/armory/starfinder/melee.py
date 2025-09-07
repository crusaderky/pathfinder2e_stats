from pathfinder2e_stats.armory._common import _weapon

# Axe
doshko = _weapon("doshko", "piercing", 12, critical="axe")
fangblade = _weapon("fangblade", "slashing", 10, boost=12, critical="axe")
plasma_doshko = _weapon("plasma_doshko", "fire", 10, critical="plasma")

# Brawling
battleglove = _weapon("battleglove", "bludgeoning", 4)
fist = _weapon("fist", "bludgeoning", 4)

# Club
baton = _weapon("baton", "bludgeoning", 6)
bone_scepter = _weapon("bone_scepter", "cold", 6)
shock_truncheon = _weapon("shock_truncheon", "electricity", 6)

# Corrosive
disintegration_lash = _weapon("disintegration lash", "acid", 6)

# Cryo
thermal_dynafan = _weapon("thermal dynafan", "fire", 6, critical="flame")
zero_knife = _weapon("zero knife", "cold", 4)

# Dart
force_needle = _weapon("force needle", "piercing", 4, critical="dart")

# Flail
battle_ribbon = _weapon("battle_ribbon", "slashing", 4)
neural_lash = _weapon("neural_lash", "mental", 8)

# Flame
skyfire_sword = _weapon("skyfire sword", "fire", 8, two_hands=10, critical="flame")

# Hammer
hammer = _weapon("hammer", "bludgeoning", 8)

# Knife
aucturnite_chakram = _weapon("aucturnite_chakram", "slashing", 6, critical="knife")
knife = _weapon("knife", "piercing", 4, critical="knife")
shooting_starknife = _weapon(
    "shooting_starknife", "piercing", 4, deadly=6, critical="knife"
)
tailblade = _weapon("tailblade", "slashing", 4, critical="knife")
talon = _weapon("talon", "acid", 6, critical="knife")

# Polearm
cryopike = _weapon("cryopike", "cold", 10)
painglaive = _weapon("painglaive", "slashing", 10, boost=10)

# Shield
shield_bash = _weapon("shield bash", "bludgeoning", 4)

# Shock
polyglove = _weapon("polyglove", "electricity", 6)
shock_pad = _weapon("shock pad", "electricity", 4)

# Sonic
pulse_gauntlet = _weapon("pulse gauntlet", "sonic", 4)

# Spear
singing_spear = _weapon("singing spear", "sonic", 6, boost=10)

# Sword
dueling_sword = _weapon("dueling_sword", "slashing", 8)
grindblade = _weapon("grindblade", "slashing", 8, fatal=12, critical="knife")
nano_edge_rapier = _weapon("nano_edge_rapier", "piercing", 6, deadly=8)
phase_cutlass = _weapon("phase_cutlass", "slashing", 6, deadly=6)
plasma_sword = _weapon("plasma_sword", "fire", 8, critical="plasma")
puzzleblade = _weapon("puzzleblade", "slashing", 8)
