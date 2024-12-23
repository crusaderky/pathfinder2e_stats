import pytest

from types import ModuleType
import pathfinder2e_stats.armory as armory
from pathfinder2e_stats import Damage, DamageList, ExpandedDamage, DoS

mods = [mod for mod in armory.__dict__.values() if isinstance(mod, ModuleType)]
funcs = [getattr(mod, name) for mod in mods for name in mod.__all__]
weapon_mods = (armory.picks, armory.swords) 
spell_mods = (armory.cantrips, armory.spells)


@pytest.mark.parametrize("func", funcs)
def test_armory(func):
    assert isinstance(func(), (Damage, DamageList, ExpandedDamage))

@pytest.mark.parametrize("func", [getattr(mod, name) for mod in weapon_mods for name in mod.__all__])

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


@pytest.mark.parametrize("func", [getattr(mod, name) for mod in spell_mods for name in mod.__all__])
def test_spells(func):
    smin = func()
    s10 = func(rank=10)
    assert s10 != smin


@pytest.mark.parametrize("func", [getattr(armory.picks, name) for name in armory.picks.__all__])
def test_picks(func):
    pick = func(dice=2, bonus=5)
    assert isinstance(pick, Damage)
    assert pick.bonus == 5

    assert func(dice=2, bonus=5, critical_specialization=True) == pick + {
        DoS.critical_success: [Damage("piercing", 0, 0, 4)]
    }

    assert func(dice=2, bonus=5, critical_specialization=True, grievous=True) == pick + {
        DoS.critical_success: [Damage("piercing", 0, 0, 8)]
    }

    # Grievous without critical specialization does nothing
    assert func(dice=2, bonus=5, grievous=True) == pick


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
