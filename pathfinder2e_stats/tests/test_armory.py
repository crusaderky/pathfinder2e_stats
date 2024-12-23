from types import ModuleType

import pytest

import pathfinder2e_stats.armory as armory
from pathfinder2e_stats import Damage, DamageList, ExpandedDamage

mods = [
    mod
    for mod in armory.__dict__.values()
    if isinstance(mod, ModuleType) and mod is not armory._common
]
weapon_mods = (
    armory.bows,
    armory.crossbows,
    armory.darts,
    armory.knives,
    armory.picks,
    armory.swords,
)
spell_mods = (armory.cantrips, armory.spells)


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
    for dos in (1, 2):
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


def test_force_barrage():
    assert armory.spells.force_barrage(actions=1) == Damage("force", 1, 4, 1)
    assert armory.spells.force_barrage(actions=2) == Damage("force", 2, 4, 2)
    assert armory.spells.force_barrage(actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=2, actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=3, actions=3) == Damage("force", 6, 4, 6)
