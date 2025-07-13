from types import ModuleType

import pytest

from pathfinder2e_stats import Damage, DamageList, DoS, ExpandedDamage, armory

mods = [
    mod
    for mod in armory.__dict__.values()
    if isinstance(mod, ModuleType) and mod is not armory._common
]
weapon_mods = [
    armory.axes,
    armory.bows,
    armory.crossbows,
    armory.darts,
    armory.hammers,
    armory.knives,
    armory.picks,
    armory.swords,
]
spell_mods = [armory.cantrips, armory.spells]
other_mods = [armory.class_features, armory.runes]


def test_mods_inventory():
    assert set(mods) == set(weapon_mods) | set(spell_mods) | set(other_mods)


@pytest.mark.parametrize(
    "func",
    [
        getattr(mod, name)
        for mod in mods
        for name in mod.__all__
        if name != "critical_specialization"
    ],
)
def test_armory(func):
    assert isinstance(func(), Damage | DamageList | ExpandedDamage)


@pytest.mark.parametrize(
    "func",
    [
        getattr(mod, name)
        for mod in weapon_mods
        for name in mod.__all__
        if name != "critical_specialization"
    ],
)
def test_weapons(func):
    w = func()
    assert w.dice == 1
    assert w.bonus == 0

    w = func(2)
    assert w.dice == 2
    assert w.bonus == 0

    w = func(2, 3)
    assert w.dice == 2
    assert w.bonus == 3


@pytest.mark.parametrize(
    "func", [getattr(mod, name) for mod in spell_mods for name in mod.__all__]
)
def test_spells(func):
    smin = func()
    s10 = func(rank=10)
    assert s10 != smin


@pytest.mark.parametrize("mod", [armory.darts, armory.crossbows, armory.knives])
def test_critical_specialization_bleed(mod):
    w = mod.critical_specialization(123)
    assert w == {2: [Damage("bleed", 1, 6, 123, persistent=True)]}


def test_critical_specialization_grievous_darts():
    w = armory.darts.critical_specialization(123, grievous=True)
    assert w == {2: [Damage("bleed", 2, 6, 123, persistent=True)]}


def test_critical_specialization_picks():
    w = armory.picks.critical_specialization(3)
    assert w == {2: [Damage("piercing", 0, 0, 6)]}

    w = armory.picks.critical_specialization(3, grievous=True)
    assert w == {2: [Damage("piercing", 0, 0, 12)]}

    # Grievous pick, switchscythe, some barbarians can change the damage type
    w = armory.picks.critical_specialization(2, type="slashing")
    assert w == {2: [Damage("slashing", 0, 0, 4)]}


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


def test_sneak_attack():
    sa = armory.class_features.sneak_attack
    assert sa(1) == Damage("precision", 1, 6)
    assert sa(4) == Damage("precision", 1, 6)
    assert sa(5) == Damage("precision", 2, 6)
    assert sa(20) == Damage("precision", 4, 6)
    assert sa(dedication=True) == Damage("precision", 1, 4)
    assert sa(5, dedication=True) == Damage("precision", 1, 4)
    assert sa(6, dedication=True) == Damage("precision", 1, 6)
    assert sa(20, dedication=True) == Damage("precision", 1, 6)


def test_precise_strike():
    ps = armory.class_features.precise_strike
    assert ps(1) == Damage("precision", 0, 0, 2)
    assert ps(4) == Damage("precision", 0, 0, 2)
    assert ps(5) == Damage("precision", 0, 0, 3)
    assert ps(20) == Damage("precision", 0, 0, 6)
    assert ps(dedication=True) == Damage("precision", 0, 0, 1)
    assert ps(20, dedication=True) == Damage("precision", 0, 0, 1)


def test_finisher():
    f = armory.class_features.finisher
    assert f(1) == Damage("precision", 2, 6)
    assert f(4) == Damage("precision", 2, 6)
    assert f(5) == Damage("precision", 3, 6)
    assert f(20) == Damage("precision", 6, 6)
    assert f(dedication=True) == Damage("precision", 1, 6)
    assert f(20, dedication=True) == Damage("precision", 1, 6)
