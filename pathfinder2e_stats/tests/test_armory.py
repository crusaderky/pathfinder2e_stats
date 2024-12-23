from types import ModuleType

import pytest

import pathfinder2e_stats.armory as armory
from pathfinder2e_stats import Damage, DamageList, DoS, ExpandedDamage

mods = [
    mod
    for mod in armory.__dict__.values()
    if isinstance(mod, ModuleType) and mod is not armory._common
]
funcs = [getattr(mod, name) for mod in mods for name in mod.__all__]
weapon_mods = (
    armory.bows,
    armory.crossbows,
    armory.darts,
    armory.knives,
    armory.picks,
    armory.swords,
)
spell_mods = (armory.cantrips, armory.spells)


@pytest.mark.parametrize("func", funcs)
def test_armory(func):
    assert isinstance(func(), Damage | DamageList | ExpandedDamage)


@pytest.mark.parametrize(
    "func", [getattr(mod, name) for mod in weapon_mods for name in mod.__all__]
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


@pytest.mark.parametrize(
    "func", [getattr(armory.picks, name) for name in armory.picks.__all__]
)
def test_picks(func):
    pick = func(dice=2, bonus=5)
    assert isinstance(pick, Damage)
    assert pick.bonus == 5

    assert func(dice=2, bonus=5, critical_specialization=True) == pick + {
        DoS.critical_success: [Damage("piercing", 0, 0, 4)]
    }

    assert func(
        dice=2, bonus=5, critical_specialization=True, grievous=True
    ) == pick + {DoS.critical_success: [Damage("piercing", 0, 0, 8)]}

    # Grievous without critical specialization does nothing
    assert func(dice=2, bonus=5, grievous=True) == pick


@pytest.mark.parametrize(
    "func",
    [
        getattr(mod, name)
        for mod in (armory.knives, armory.darts, armory.crossbows)
        for name in mod.__all__
    ],
)
def test_bleed_on_crit_weapons(func):
    if func.__name__ == "sukgung":
        pytest.skip(reason="fatal aim")

    w = func()
    assert isinstance(w, Damage)

    # FIXME
    if func.__name__ == "sukgung":
        with pytest.warns(UserWarning, match="two hands"):  # FIXME
            w = func(critical_specialization=True, item_attack_bonus=123)
    else:
        w = func(critical_specialization=True, item_attack_bonus=123)

    assert isinstance(w, ExpandedDamage)
    assert w[DoS.critical_success][-1] == Damage("bleed", 1, 6, 123, persistent=True)


@pytest.mark.parametrize("hands", [1, 2])
def test_sukgung(hands):
    w = armory.crossbows.sukgung().hands(hands=hands)
    assert isinstance(w, Damage)
    w = armory.crossbows.sukgung(
        critical_specialization=True, item_attack_bonus=123, hands=hands
    )
    assert isinstance(w, ExpandedDamage)
    assert w[DoS.critical_success][-1] == Damage("bleed", 1, 6, 123, persistent=True)


def test_sukgung_implicit_hands():
    w1 = armory.crossbows.sukgung(
        critical_specialization=True, item_attack_bonus=123, hands=2
    )
    with pytest.warns(UserWarning, match="two hands"):
        w2 = armory.crossbows.sukgung(
            critical_specialization=True, item_attack_bonus=123
        )
    assert w1 == w2


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


def test_force_barrage():
    assert armory.spells.force_barrage(actions=1) == Damage("force", 1, 4, 1)
    assert armory.spells.force_barrage(actions=2) == Damage("force", 2, 4, 2)
    assert armory.spells.force_barrage(actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=2, actions=3) == Damage("force", 3, 4, 3)
    assert armory.spells.force_barrage(rank=3, actions=3) == Damage("force", 6, 4, 6)
