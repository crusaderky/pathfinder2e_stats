from pathfinder2e_stats.armory._common import _weapon
from pathfinder2e_stats.damage_spec import Damage

# Bow
bow_staff = _weapon("bow_staff", "piercing", 6, deadly=8)
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
air_repeater = _weapon("air_repeater", "piercing", 4)
arquebus = _weapon("arquebus", "piercing", 8, fatal=10)
axe_musket = _weapon("axe_musket", "piercing", 6, fatal=10)
barricade_buster = _weapon("barricade_buster", "bludgeoning", 10)
big_boom_gun = _weapon("big_boom_gun", "piercing", 6, fatal=12)
black_powder_knuckle_dusters = _weapon(
    "black_powder_knuckle_dusters", "piercing", 4, fatal=8
)
blunderbuss = _weapon("blunderbuss", "piercing", 8, scatter=True)
cane_pistol = _weapon("cane_pistol", "piercing", 4, fatal=8)
clan_pistol = _weapon("clan_pistol", "piercing", 6, fatal=10)
coat_pistol = _weapon("coat_pistol", "piercing", 4, fatal=8)
dagger_pistol = _weapon("dagger_pistol", "piercing", 4, fatal=8)
dawnsilver_tree = _weapon("dawnsilver_tree", "piercing", 6, fatal=10)
double_barreled_musket = _weapon("double_barreled_musket", "piercing", 6, fatal=10)
double_barreled_pistol = _weapon("double_barreled_pistol", "piercing", 4, fatal=8)
dragon_mouth_pistol = _weapon("dragon_mouth_pistol", "piercing", 6, scatter=True)
dueling_pistol = _weapon("dueling_pistol", "piercing", 6, fatal=10)
dwarven_scattergun = _weapon(
    "dwarven_scattergun", "piercing", 8, kickback=True, scatter=True
)
explosive_dogslicer = _weapon(
    "explosive_dogslicer", "slashing", 6, fatal=10, scatter=True
)
fire_lance = _weapon("fire_lance", "piercing", 6, fatal=10)
flingflenser = _weapon("flingflenser", "slashing", 6, fatal=10, scatter=True)
flintlock_musket = _weapon("flintlock_musket", "piercing", 6, fatal=10)
flintlock_pistol = _weapon("flintlock_pistol", "piercing", 4, fatal=8)
gnome_amalgam_musket = _weapon("gnome_amalgam_musket", "piercing", 6, fatal=10)
gun_sword = _weapon("gun_sword", "piercing", 10, kickback=True)
hammer_gun = _weapon("hammer_gun", "piercing", 6, fatal=10)
hand_cannon = _weapon("hand_cannon", "piercing", 6)
harmona_gun = _weapon("harmona_gun", "bludgeoning", 10, kickback=True)
jezail = _weapon("jezail", "piercing", 8, fatal_aim=12)
long_air_repeater = _weapon("long_air_repeater", "piercing", 4, kickback=True)
mace_multipistol = _weapon("mace_multipistol", "piercing", 4, fatal=8)
pepperbox = _weapon("pepperbox", "piercing", 4, fatal=8)
piercing_wind = _weapon("piercing_wind", "piercing", 6, fatal_aim=10)
rapier_pistol = _weapon("rapier_pistol", "piercing", 4, fatal=8)
shield_pistol = _weapon("shield_pistol", "piercing", 4, fatal=8)
slide_pistol = _weapon("slide_pistol", "piercing", 6, fatal=10)
spoon_gun = _weapon("spoon_gun", "piercing", 4, scatter=True)
three_peaked_tree = _weapon("three_peaked_tree", "piercing", 6, fatal=10)
triggerbrand = _weapon("triggerbrand", "piercing", 4, fatal=8)

# Knife
chakram = _weapon("chakram", "slashing", 8, critical="knife")

# Sling
backpack_catapult = _weapon("backpack_catapult", "bludgeoning", 12)
bola = _weapon("bola", "bludgeoning", 6)
halfling_sling_staff = _weapon("halfling_sling_staff", "bludgeoning", 10)
kestros = _weapon("kestros", "piercing", 6)
sling = _weapon("sling", "bludgeoning", 6)
spraysling = _weapon("spraysling", "bludgeoning", 6, scatter=True)
sun_sling = _weapon("sun_sling", "piercing", 8)
thunder_sling = _weapon("thunder_sling", "piercing", 6)
wrecker = _weapon("wrecker", "bludgeoning", 6)
