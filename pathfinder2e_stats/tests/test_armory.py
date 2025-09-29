import warnings
from types import ModuleType

import pytest

from pathfinder2e_stats import Damage, DamageList, DoS, ExpandedDamage, armory

mods = [
    mod
    for package in (armory, armory.class_features, armory.pathfinder, armory.starfinder)
    for mod in package.__dict__.values()
    if isinstance(mod, ModuleType)
    and mod
    not in (
        armory._common,
        armory.class_features,
        armory.pathfinder,
        armory.starfinder,
        warnings,
    )
]

weapon_mods = [
    armory.pathfinder.melee,
    armory.pathfinder.ranged,
    armory.starfinder.melee,
    armory.starfinder.ranged,
]
class_feature_mods = [
    armory.class_features.operative,
    armory.class_features.rogue,
    armory.class_features.swashbuckler,
]
spell_mods = [armory.cantrips, armory.spells]
other_mods = [armory.critical_specialization, armory.runes]


def test_mods_inventory():
    assert set(mods) == {
        m
        for mm in (weapon_mods, class_feature_mods, spell_mods, other_mods)
        for m in mm
    }


@pytest.mark.parametrize(
    "func",
    [
        pytest.param(getattr(mod, name), id=f"{mod.__name__}.{name}")
        for mod in mods
        for name in mod.__all__
        if mod is not armory.critical_specialization
        and not (mod is armory.class_features.operative and name == "critical_aim")
    ],
)
def test_armory(func):
    assert isinstance(func(), Damage | DamageList | ExpandedDamage)


def test_autodoc():
    assert ":prd:`Fireball`" in armory.spells.fireball.__doc__
    assert ":prd:`Battle Axe`" in armory.pathfinder.melee.battle_axe.__doc__
    assert "1d8 slashing" in armory.pathfinder.melee.battle_axe.__doc__
    assert ":prd:`Greataxe`" in armory.pathfinder.melee.greataxe.__doc__
    assert ":srd:`Baton`" in armory.starfinder.melee.baton.__doc__


@pytest.mark.parametrize("mod", [*mods, armory, armory.starfinder])
def test_dir(mod):
    """Test that the dir() output, used by IPython autocompletion,
    does not return any internal objects.
    """
    d = dir(mod)
    assert len(d) == len(set(d)), "duplicates found"
    for name in d:
        # _ and __ names are not a problem as they are not suggested by IPython
        assert name.startswith("_") or name[0].islower(), name


@pytest.mark.parametrize(
    "func", [getattr(mod, name) for mod in weapon_mods for name in mod.__all__]
)
def test_weapons(func):
    w = func()

    if func in (
        armory.pathfinder.melee.fire_poi,
        armory.pathfinder.melee.macuahuitl,
        armory.pathfinder.ranged.blowgun,
        armory.pathfinder.ranged.dart_umbrella,
    ):
        return

    assert w.dice == 1
    assert w.bonus in (0, 1)  # kickback weapons deal +1 damage

    w = func(2)
    assert w.dice == 2
    assert w.bonus in (0, 1)

    w = func(2, 3)
    assert w.dice == 2
    assert w.bonus in (3, 4)


def test_kickback():
    f = armory.starfinder.ranged.seeker_rifle
    assert f() == Damage("piercing", 1, 10, 1)
    assert f(2, 3) == Damage("piercing", 2, 10, 4)


@pytest.mark.parametrize(
    "func", [armory.pathfinder.ranged.blowgun, armory.pathfinder.ranged.dart_umbrella]
)
def test_blowgun(func):
    w = func()
    assert w == Damage("piercing", 0, 0, 1)
    w = func(10, 20)
    assert w == Damage("piercing", 0, 0, 21)


def test_macuahuitl():
    f = armory.pathfinder.melee.macuahuitl
    assert f() == Damage("slashing", 1, 8) + Damage("bleed", 0, 0, 1, persistent=True)
    assert f(2, 10) == Damage("slashing", 2, 8, 10) + Damage(
        "bleed", 0, 0, 1, persistent=True
    )
    assert f(3, 10) == Damage("slashing", 3, 8, 10) + Damage(
        "bleed", 0, 0, 2, persistent=True
    )


def test_fire_poi():
    f = armory.pathfinder.melee.fire_poi
    assert f() == (
        Damage("bludgeoning", 1, 4)
        + Damage("fire", 1, 4)
        + {DoS.critical_success: [Damage("fire", 0, 0, 1, persistent=True)]}
    )
    assert f(2, 3) == (
        Damage("bludgeoning", 2, 4, 3)
        + Damage("fire", 1, 4)
        + {DoS.critical_success: [Damage("fire", 0, 0, 1, persistent=True)]}
    )


@pytest.mark.parametrize(
    "func", [getattr(mod, name) for mod in spell_mods for name in mod.__all__]
)
def test_spells(func):
    smin = func()
    s10 = func(rank=10)
    assert s10 != smin


@pytest.mark.parametrize(
    "group,faces,type_",
    [
        ("crossbow", 8, "bleed"),
        ("dart", 6, "bleed"),
        ("knife", 6, "bleed"),
        ("flame", 6, "fire"),
        ("plasma", 6, "electricity"),
    ],
)
def test_critical_specialization_persistent_damage(group, faces, type_):
    func = getattr(armory.critical_specialization, group)
    w = func(123)
    assert w == {2: [Damage(type_, 1, faces, 123, persistent=True)]}
    assert f"1d{faces} persistent {type_}" in func.__doc__


def test_critical_specialization_grievous_dart():
    w = armory.critical_specialization.dart(123, grievous=True)
    assert w == {2: [Damage("bleed", 2, 6, 123, persistent=True)]}


def test_critical_specialization_axe():
    # bonus, deadly, fatal, etc. are discarded
    base = Damage("slashing", 2, 12, 6, deadly=8, fatal=12)
    w = armory.critical_specialization.axe(base)
    assert w == {2: [Damage("slashing", 2, 12)]}

    # two-hands
    base = Damage("slashing", 2, 8, 4, two_hands=12)
    with pytest.warns(UserWarning, match="two hands"):
        w = armory.critical_specialization.axe(base)
    assert w == {2: [Damage("slashing", 2, 12)]}
    w = armory.critical_specialization.axe(base.hands(1))
    assert w == {2: [Damage("slashing", 2, 8)]}
    w = armory.critical_specialization.axe(base.hands(2))
    assert w == {2: [Damage("slashing", 2, 12)]}

    # Property runes, precision, etc.
    base = Damage("slashing", 2, 12, 4) + Damage("precision", 0, 0, 1)
    with pytest.raises(ValueError, match="property runes"):
        armory.critical_specialization.axe(base)


def test_critical_specialization_pick():
    w = armory.critical_specialization.pick(3)
    assert w == {2: [Damage("piercing", 0, 0, 6)]}

    w = armory.critical_specialization.pick(3, grievous=True)
    assert w == {2: [Damage("piercing", 0, 0, 12)]}

    # Grievous pick, switchscythe, some barbarians can change the damage type
    w = armory.critical_specialization.pick(2, type="slashing")
    assert w == {2: [Damage("slashing", 0, 0, 4)]}


def test_critical_specialization_sniper():
    w = armory.critical_specialization.sniper(3)
    assert w == {2: [Damage("piercing", 0, 0, 6)]}

    # Grievous pick, switchscythe, some barbarians can change the damage type
    w = armory.critical_specialization.sniper(2, type="fire")
    assert w == {2: [Damage("fire", 0, 0, 4)]}


def test_ignition():
    ir = armory.cantrips.ignition()
    im = armory.cantrips.ignition(melee=True)
    for dos in (DoS.success, DoS.critical_success):
        for el in ir[dos]:
            assert el.faces == 4
        for el in im[dos]:
            assert el.faces == 6


def test_shocking_grasp():
    nonmetal = armory.spells.shocking_grasp()
    metal = armory.spells.shocking_grasp(metal=True)
    assert isinstance(nonmetal, Damage)
    assert isinstance(metal, ExpandedDamage)
    assert nonmetal.expand() != metal


def test_blazing_bolt():
    assert armory.spells.blazing_bolt(actions=1) == Damage("fire", 2, 6)
    assert armory.spells.blazing_bolt(actions=2) == Damage("fire", 4, 6)
    assert armory.spells.blazing_bolt(actions=3) == Damage("fire", 4, 6)
    assert armory.spells.blazing_bolt(rank=3, actions=1) == Damage("fire", 3, 6)
    assert armory.spells.blazing_bolt(rank=3, actions=2) == Damage("fire", 6, 6)
    assert armory.spells.blazing_bolt(rank=3, actions=3) == Damage("fire", 6, 6)


def test_dehydrate():
    assert armory.spells.dehydrate().dice == 1
    assert armory.spells.dehydrate(rank=2).dice == 1
    assert armory.spells.dehydrate(rank=3).dice == 4
    assert armory.spells.dehydrate(rank=4).dice == 4
    assert armory.spells.dehydrate(rank=5).dice == 7


def test_divine_wrath():
    d = armory.spells.divine_wrath()
    assert d[DoS.failure] == d[DoS.critical_failure]  # Doesn't double


def test_force_barrage():
    assert armory.spells.force_barrage(actions=1) == Damage("force", 1, 4, 1)
    assert armory.spells.force_barrage(actions=2) == Damage("force", 2, 4, 2)
    assert armory.spells.force_barrage(actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=2, actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=3, actions=3) == Damage("force", 6, 4, 6)
    assert armory.spells.force_barrage(
        rank=3, actions=3, corageous_anthem=True
    ) == Damage("force", 6, 4, 12)


def test_harm_heal():
    assert armory.spells.harm().faces == 8
    assert armory.spells.harm(harming_hands=True).faces == 10
    assert armory.spells.heal().faces == 8
    assert armory.spells.heal(healing_hands=True).faces == 10


@pytest.mark.parametrize(
    "func",
    [
        pytest.param(getattr(mod, name), id=f"{mod.__name__}.{name}")
        for mod in class_feature_mods
        for name in mod.__all__
        if not (mod is armory.class_features.operative and name == "critical_aim")
    ],
)
def test_class_features(func):
    d = func()
    for level in range(1, 21):
        d2 = func(level)
        assert type(d2) is type(d)


def test_aim():
    aim = armory.class_features.operative.aim
    # Bump at level 5, 11, and 17
    assert aim(1) == Damage("precision", 1, 4)
    assert aim(4) == Damage("precision", 1, 4)
    assert aim(5) == Damage("precision", 2, 4)
    assert aim(16) == Damage("precision", 3, 4)
    assert aim(17) == Damage("precision", 4, 4)
    assert aim(20) == Damage("precision", 4, 4)

    assert aim(20, devastating_aim=True) == Damage("precision", 4, 6)
    assert aim(4, dedication=True) == Damage("precision", 1, 4)
    assert aim(6, dedication=True) == Damage("precision", 2, 4)
    assert aim(20, dedication=True) == Damage("precision", 2, 4)
    assert aim(20, devastating_aim=True, dedication=True) == Damage("precision", 2, 6)


def test_bloody_wounds():
    bw = armory.class_features.operative.bloody_wounds

    def crit_bleed(n: int) -> ExpandedDamage:
        return ExpandedDamage(
            {DoS.critical_success: [Damage("bleed", 0, 0, n, persistent=True)]}
        )

    # Bump at level 5, 11, and 17
    assert bw(4) == crit_bleed(1)
    assert bw(5) == crit_bleed(2)
    assert bw(16) == crit_bleed(3)
    assert bw(17) == crit_bleed(4)
    assert bw(20) == crit_bleed(4)

    assert bw(4, dedication=True) == crit_bleed(1)
    assert bw(5, dedication=True) == crit_bleed(1)
    assert bw(6, dedication=True) == crit_bleed(2)
    assert bw(20, dedication=True) == crit_bleed(2)


def test_critical_aim():
    ca = armory.class_features.operative.critical_aim
    a = armory.critical_specialization.dart(123)
    b = ca(a)
    assert b == ExpandedDamage(
        {DoS.success: [Damage("bleed", 1, 6, 123, persistent=True)]}
    )

    with pytest.raises(ValueError, match="critical specialization"):
        ca(Damage("piercing", 1, 6))
    with pytest.raises(ValueError, match="critical specialization"):
        ca(Damage("piercing", 1, 6).expand())


def test_sneak_attack():
    sa = armory.class_features.rogue.sneak_attack
    assert sa(1) == Damage("precision", 1, 6)
    assert sa(4) == Damage("precision", 1, 6)
    assert sa(5) == Damage("precision", 2, 6)
    assert sa(20) == Damage("precision", 4, 6)
    assert sa(dedication=True) == Damage("precision", 1, 4)
    assert sa(5, dedication=True) == Damage("precision", 1, 4)
    assert sa(6, dedication=True) == Damage("precision", 1, 6)
    assert sa(20, dedication=True) == Damage("precision", 1, 6)


def test_precise_strike():
    ps = armory.class_features.swashbuckler.precise_strike
    assert ps(1) == Damage("precision", 0, 0, 2)
    assert ps(4) == Damage("precision", 0, 0, 2)
    assert ps(5) == Damage("precision", 0, 0, 3)
    assert ps(20) == Damage("precision", 0, 0, 6)
    assert ps(dedication=True) == Damage("precision", 0, 0, 1)
    assert ps(20, dedication=True) == Damage("precision", 0, 0, 1)


def test_finisher():
    f = armory.class_features.swashbuckler.finisher
    assert f(1) == Damage("precision", 2, 6)
    assert f(4) == Damage("precision", 2, 6)
    assert f(5) == Damage("precision", 3, 6)
    assert f(20) == Damage("precision", 6, 6)
    assert f(dedication=True) == Damage("precision", 1, 6)
    assert f(20, dedication=True) == Damage("precision", 1, 6)


def test_deprecations_class_features():
    """Functions moved in 0.2.0"""
    with pytest.raises(AttributeError):
        _ = armory.class_features.aim  # Not in 0.1.1

    assert "sneak_attack" not in dir(armory.class_features)
    with pytest.warns(FutureWarning, match="moved to"):
        cf = armory.class_features.sneak_attack
    assert cf is armory.class_features.rogue.sneak_attack

    assert "precise_strike" not in dir(armory.class_features)
    with pytest.warns(FutureWarning, match="moved to"):
        cf = armory.class_features.precise_strike
    assert cf is armory.class_features.swashbuckler.precise_strike


def test_deprecations_weapons():
    """Functions moved in 0.2.0"""
    with pytest.raises(AttributeError):
        _ = armory.polearms  # Not in 0.1.1

    assert "axes" not in dir(armory)
    with pytest.warns(FutureWarning, match="has been split into"):
        w = armory.axes.greataxe
    assert w is armory.pathfinder.melee.greataxe

    with pytest.warns(FutureWarning, match="has been split into"):
        w = armory.crossbows.crossbow
    assert w is armory.pathfinder.ranged.crossbow

    with pytest.warns(FutureWarning, match="has been split into"):
        cs = armory.crossbows.critical_specialization
    assert cs is armory.critical_specialization.crossbow

    with pytest.warns(FutureWarning, match="has been split into"):
        cs = armory.darts.critical_specialization
    assert cs is armory.critical_specialization.dart

    with pytest.warns(FutureWarning, match="has been split into"):
        cs = armory.knives.critical_specialization
    assert cs is armory.critical_specialization.knife

    with pytest.warns(FutureWarning, match="has been split into"):
        cs = armory.picks.critical_specialization
    assert cs is armory.critical_specialization.pick
