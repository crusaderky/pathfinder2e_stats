from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.damage_spec import Damage, DamageList

# Axe
adze = _weapon("adze", "slashing", 10, critical="axe")
battle_axe = _weapon("battle_axe", "slashing", 8, critical="axe")
battle_saddle = _weapon("battle_saddle", "slashing", 8, critical="axe")
boarding_axe = _weapon("boarding_axe", "slashing", 6, critical="axe")
butchering_axe = _weapon("butchering_axe", "slashing", 12, critical="axe")
dwarven_waraxe = _weapon("dwarven_waraxe", "slashing", 8, two_hands=12, critical="axe")
greataxe = _weapon("greataxe", "slashing", 12, critical="axe")
hand_adze = _weapon("hand_adze", "slashing", 4, critical="axe")
hatchet = _weapon("hatchet", "slashing", 6, critical="axe")
mambele = _weapon("mambele", "slashing", 6, deadly=8, critical="axe")
orc_necksplitter = _weapon("orc_necksplitter", "slashing", 8, critical="axe")
palstave = _weapon("palstave", "slashing", 6, critical="axe")
panabas = _weapon("panabas", "slashing", 6, two_hands=10, critical="axe")

# Brawling
bladed_gauntlet = _weapon("bladed_gauntlet", "slashing", 4)
fangwire = _weapon("fangwire", "slashing", 4, deadly=8)
fist = _weapon("fist", "bludgeoning", 4)
gauntlet = _weapon("gauntlet", "bludgeoning", 4)
gauntlet_bow = _weapon("gauntlet_bow", "bludgeoning", 4)  # Melee use
knuckle_duster = _weapon("knuckle_duster", "bludgeoning", 4)
pantograph_gauntlet = _weapon("pantograph_gauntlet", "bludgeoning", 4, deadly=6)
spiked_gauntlet = _weapon("spiked_gauntlet", "piercing", 4)
tekko_kagi = _weapon("tekko_kagi", "slashing", 4)
thorn_whip = _weapon("thorn_whip", "piercing", 4)
tonfa = _weapon("tonfa", "bludgeoning", 4)
tri_bladed_katar = _weapon("tri_bladed_katar", "piercing", 4, fatal=8)

# Club
aklys = _weapon("aklys", "bludgeoning", 6)
battle_lute = _weapon("battle_lute", "bludgeoning", 4, two_hands=8)
bo_staff = _weapon("bo_staff", "bludgeoning", 8)
clockwork_macuahuitl = _weapon("clockwork_macuahuitl", "slashing", 10)
club = _weapon("club", "bludgeoning", 6)
cruuk = _weapon("cruuk", "bludgeoning", 6)
exquisite_sword_cane_sheath = _weapon("exquisite_sword_cane_sheath", "bludgeoning", 4)
fighting_stick = _weapon("fighting_stick", "bludgeoning", 6)
frying_pan = _weapon("frying_pan", "bludgeoning", 4, fatal=8)
gada = _weapon("gada", "bludgeoning", 8, two_hands=12)
gaff = _weapon("gaff", "bludgeoning", 6)
greatclub = _weapon("greatclub", "bludgeoning", 10)
griffon_cane = _weapon("griffon_cane", "bludgeoning", 6, two_hands=10)
juggling_club = _weapon("juggling_club", "bludgeoning", 4)
khakkhara = _weapon("khakkhara", "bludgeoning", 6, two_hands=10)
leiomano = _weapon("leiomano", "bludgeoning", 6, fatal=10)
light_mace = _weapon("light_mace", "bludgeoning", 4)
mace = _weapon("mace", "bludgeoning", 6)
maul_spade = _weapon("maul_spade", "bludgeoning", 10, deadly=10)
morningstar = _weapon("morningstar", "bludgeoning", 6)
nightstick = _weapon("nightstick", "bludgeoning", 4)
nunchaku = _weapon("nunchaku", "bludgeoning", 6)
probing_cane = _weapon("probing_cane", "bludgeoning", 6)
reinforced_frame = _weapon("reinforced_frame", "bludgeoning", 4)
reinforced_stock = _weapon("reinforced_stock", "bludgeoning", 4, two_hands=8)
sap = _weapon("sap", "bludgeoning", 6)
staff = _weapon("staff", "bludgeoning", 4, two_hands=8)
tetsubo = _weapon("tetsubo", "bludgeoning", 10)
thundermace = _weapon("thundermace", "bludgeoning", 8)
war_gavel = _weapon("war_gavel", "bludgeoning", 6)
whipstaff = _weapon("whipstaff", "bludgeoning", 6)


def macuahuitl(dice: int = 1, bonus: int = 0) -> DamageList:
    """:prd_traits:`Tearing <841>`:
    This weapon is edged with curved teeth that leave bleeding wounds. When you hit a
    creature with this weapon, it deals an additional 1 persistent bleed damage. This
    increases to 2 persistent bleed damage if the weapon has a greater striking rune.
    """
    return DamageList(
        [
            Damage("slashing", dice, 8, bonus),
            Damage("bleed", 0, 0, 2 if dice > 2 else 1, persistent=True),
        ]
    )


# Dart
rope_dart = _weapon("rope_dart", "piercing", 4, critical="dart")
stiletto_pen = _weapon("stiletto_pen", "piercing", 4, critical="dart")
tamchal_chakram = _weapon("tamchal_chakram", "slashing", 6, deadly=6, critical="dart")
war_javelin = _weapon("war_javelin", "piercing", 6, critical="dart")

# Firearm
# TODO melee use of combination weapons

# Flail
mikazuki = _weapon("mikazuki", "bludgeoning", 6)
# TODO missing entries

# Hammer
earthbreaker = _weapon("earthbreaker", "bludgeoning", 6, two_hands=10)
gnome_hooked_hammer = _weapon("gnome_hooked_hammer", "bludgeoning", 6, two_hands=10)
light_hammer = _weapon("light_hammer", "bludgeoning", 6)
long_hammer = _weapon("long_hammer", "bludgeoning", 8)
maul = _weapon("maul", "bludgeoning", 12)
orc_skewermaul = _weapon("orc_skewermaul", "bludgeoning", 6, two_hands=10)
warhammer = _weapon("warhammer", "bludgeoning", 8)

# Knife
dagger = _weapon("dagger", "piercing", 4, critical="knife")
kama = _weapon("kama", "slashing", 6, critical="knife")
kukri = _weapon("kukri", "slashing", 6, critical="knife")
flyssa = _weapon("flyssa", "piercing", 6, critical="knife")
sickle = _weapon("sickle", "slashing", 4, critical="knife")
# TODO missing entries

# Pick
greatpick = _weapon("greatpick", "piercing", 10, fatal=12, critical="pick")
light_pick = _weapon("light_pick", "piercing", 4, fatal=8, critical="pick")
ogre_hook = _weapon("ogre_hook", "piercing", 10, deadly=10, critical="pick")
pick = _weapon("pick", "piercing", 6, fatal=10, critical="pick")
switchscythe = _weapon("switchscythe", "piercing", 6, fatal=10, critical="pick")
tricky_pick = _weapon("tricky_pick", "piercing", 6, fatal=10, critical="pick")

# Polearm
# TODO missing entries

# Shield
shield_bash = _weapon("shield bash", "bludgeoning", 4)
shield_boss = _weapon("shield boss", "bludgeoning", 6)
shield_spikes = _weapon("shield spikes", "piercing", 6)

# Sling
# TODO melee use of combination weapons

# Spear
lancer = _weapon("lancer", "piercing", 6)
# TODO missing entries

# Sword
shortsword = _weapon("shortsword", "slashing", 6)
rapier = _weapon("rapier", "piercing", 6, deadly=8)
longsword = _weapon("longsword", "slashing", 8)
bastard_sword = _weapon("bastard_sword", "slashing", 8, two_hands=12)
greatsword = _weapon("greatsword", "slashing", 12)
# TODO missing entries
