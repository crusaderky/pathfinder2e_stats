from pathfinder2e_stats.armory._common import _weapon

# Axe
battle_axe = _weapon("battle_axe", "slashing", 8, critical="axe")
dwarven_waraxe = _weapon("dwarven_waraxe", "slashing", 8, two_hands=12, critical="axe")
greataxe = _weapon("greataxe", "slashing", 12, critical="axe")
hatchet = _weapon("hatchet", "slashing", 6, critical="axe")

# Brawling
bladed_gauntlet = _weapon("bladed_gauntlet", "slashing", 4)
fangwire = _weapon("fangwire", "slashing", 4, deadly=8)
fist = _weapon("fist", "bludgeoning", 4)
gauntlet = _weapon("gauntlet", "bludgeoning", 4)
knuckle_duster = _weapon("knuckle_duster", "bludgeoning", 4)
pantograph_gauntlet = _weapon("pantograph_gauntlet", "bludgeoning", 4, deadly=6)
spiked_gauntlet = _weapon("spiked_gauntlet", "piercing", 4)
tekko_kagi = _weapon("tekko_kagi", "slashing", 4)
thorn_whip = _weapon("thorn_whip", "piercing", 4)
tonfa = _weapon("tonfa", "bludgeoning", 4)
tri_bladed_katar = _weapon("tri_bladed_katar", "piercing", 4, fatal=8)

# Hammer
earthbreaker = _weapon("earthbreaker", "bludgeoning", 6, two_hands=10)
gnome_hooked_hammer = _weapon("gnome_hooked_hammer", "bludgeoning", 6, two_hands=10)
light_hammer = _weapon("light_hammer", "bludgeoning", 6)
long_hammer = _weapon("long_hammer", "bludgeoning", 8)
maul = _weapon("maul", "bludgeoning", 12)
warhammer = _weapon("warhammer", "bludgeoning", 8)

# Knife
dagger = _weapon("dagger", "piercing", 4, critical="knife")
kama = _weapon("kama", "slashing", 6, critical="knife")
kukri = _weapon("kukri", "slashing", 6, critical="knife")
flyssa = _weapon("flyssa", "piercing", 6, critical="knife")
sickle = _weapon("sickle", "slashing", 4, critical="knife")

# Pick
light_pick = _weapon("light_pick", "piercing", 4, fatal=8, critical="pick")
pick = _weapon("pick", "piercing", 6, fatal=10, critical="pick")
greatpick = _weapon("greatpick", "piercing", 10, fatal=12, critical="pick")
switchscythe = _weapon("switchscythe", "piercing", 6, fatal=10, critical="pick")
tricky_pick = _weapon("tricky_pick", "piercing", 6, fatal=10, critical="pick")

# Shield
shield_bash = _weapon("shield bash", "bludgeoning", 4)
shield_boss = _weapon("shield boss", "bludgeoning", 6)
shield_spikes = _weapon("shield spikes", "piercing", 6)

# Sword
shortsword = _weapon("shortsword", "slashing", 6)
rapier = _weapon("rapier", "piercing", 6, deadly=8)
longsword = _weapon("longsword", "slashing", 8)
bastard_sword = _weapon("bastard_sword", "slashing", 8, two_hands=12)
greatsword = _weapon("greatsword", "slashing", 12)
