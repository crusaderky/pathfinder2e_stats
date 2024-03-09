from __future__ import annotations

from textwrap import dedent

import pytest

from pathfinder2e_stats import Damage, DoS, ExpandedDamage


def test_damage_type_validation():
    with pytest.raises(TypeError):
        Damage(1, 6, 4)
    with pytest.raises(TypeError):
        Damage("fire", 1, 6, multiplier=True)
    with pytest.raises(TypeError):
        Damage("fire", True, 6)
    with pytest.raises(TypeError):
        Damage("fire", 1, 6, splash=1)
    Damage("fire", 1, 6, multiplier=0.5)
    Damage("fire", 1, 6, multiplier=2)


def test_damage_type_str():
    d = Damage("fire", 1, 6)
    assert str(d) == "1d6 fire"

    d = Damage("fire", 2, 6, 3)
    assert str(d) == "2d6+3 fire"

    d = Damage("fire", 2, 6, -1)
    assert str(d) == "2d6-1 fire"

    d = Damage("fire", 0, 0, 1)
    assert str(d) == "1 fire"

    d = Damage("fire", 6, 6, 1, 2)
    assert str(d) == "(6d6+1)x2 fire"

    d = Damage("fire", 6, 6, 1, 0.5)
    assert str(d) == "(6d6+1)/2 fire"

    d = Damage("fire", 0, 0, 1, persistent=True)
    assert str(d) == "1 persistent fire"

    d = Damage("fire", 0, 0, 1, splash=True)
    assert str(d) == "1 fire splash"

    d = Damage("piercing", 2, 6, 4, deadly=8)
    assert str(d) == "2d6+4 deadly d8 piercing"

    d = Damage("piercing", 2, 6, 4, fatal=10)
    assert str(d) == "2d6+4 fatal d10 piercing"

    d = Damage("fire", 6, 6, basic_save=True)
    assert str(d) == "6d6 fire, with a basic saving throw"


def test_damage_type_copy():
    d = Damage("fire", 1, 6, 3, persistent=True)
    d2 = d.copy(multiplier=2)
    assert d2 == Damage("fire", 1, 6, 3, 2, persistent=True)
    d3 = d.copy(bonus=5)
    assert d3 == Damage("fire", 1, 6, 5, persistent=True)


def test_damage_type_simplify():
    assert Damage.simplify(
        [
            Damage("piercing", 1, 6),
            Damage("fire", 0, 0, 1, splash=True),
            Damage("fire", 1, 4, persistent=True),
            Damage("piercing", 0, 0, 1),
            Damage("piercing", 2, 6, 2),
            Damage("piercing", 1, 8),
            Damage("piercing", 1, 8, multiplier=2),
        ]
    ) == [
        Damage("piercing", 1, 8, multiplier=2),
        Damage("piercing", 1, 8),
        Damage("piercing", 3, 6, 3),
        Damage("fire", 1, 4, persistent=True),
        Damage("fire", 0, 0, 1, splash=True),
    ]


@pytest.mark.parametrize("persistent", [False, True])
def test_expand_attack(persistent):
    assert Damage("slashing", 1, 6, 4, persistent=persistent).expand() == {
        1: [Damage("slashing", 1, 6, 4, persistent=persistent)],
        2: [Damage("slashing", 1, 6, 4, 2, persistent=persistent)],
    }


@pytest.mark.parametrize("persistent", [False, True])
def test_expand_basic_save(persistent):
    assert Damage("fire", 1, 6, 2, basic_save=True, persistent=persistent).expand() == {
        -1: [Damage("fire", 1, 6, 2, 2, persistent=persistent)],
        0: [Damage("fire", 1, 6, 2, persistent=persistent)],
        1: [Damage("fire", 1, 6, 2, 0.5, persistent=persistent)],
    }


def test_expand_bonus_only():
    assert Damage("fire", 0, 0, 1).expand() == {
        1: [Damage("fire", 0, 0, 1)],
        2: [Damage("fire", 0, 0, 2)],
    }
    assert Damage("fire", 0, 0, 1, basic_save=True).expand() == {
        -1: [Damage("fire", 0, 0, 2)],
        0: [Damage("fire", 0, 0, 1)],
    }
    assert Damage("fire", 0, 0, 5, basic_save=True).expand() == {
        -1: [Damage("fire", 0, 0, 10)],
        0: [Damage("fire", 0, 0, 5)],
        1: [Damage("fire", 0, 0, 2)],
    }


def test_expand_splash():
    d = Damage("fire", 1, 6, 2, splash=True)
    assert d.expand() == {0: [d], 1: [d], 2: [d]}


@pytest.mark.parametrize("dice,deadly_dice", [(1, 1), (2, 1), (3, 2), (4, 3)])
def test_expand_deadly(dice, deadly_dice):
    assert Damage("slashing", dice, 6, 4, deadly=8).expand() == {
        1: [Damage("slashing", dice, 6, 4)],
        2: [Damage("slashing", dice, 6, 4, 2), Damage("slashing", deadly_dice, 8)],
    }


def test_expand_fatal():
    assert Damage("slashing", 2, 8, 4, fatal=12).expand() == {
        1: [Damage("slashing", 2, 8, 4)],
        2: [Damage("slashing", 2, 12, 4, 2), Damage("slashing", 1, 12)],
    }


def test_expand_deadly_fatal():
    """Probably possible through some features"""
    assert Damage("slashing", 2, 8, 4, deadly=8, fatal=12).expand() == {
        1: [Damage("slashing", 2, 8, 4)],
        2: [
            Damage("slashing", 2, 12, 4, 2),
            Damage("slashing", 1, 12),
            Damage("slashing", 1, 8),
        ],
    }


def test_damage_list():
    actual = Damage("slashing", 1, 6, 2) + Damage("slashing", 0, 0, 3)
    assert actual == [Damage("slashing", 1, 6, 5)]
    assert str(actual) == "1d6+5 slashing"

    actual = Damage("slashing", 1, 6, 2) + Damage("fire", 1, 6)
    assert actual == [Damage("slashing", 1, 6, 2), Damage("fire", 1, 6)]
    assert str(actual) == "1d6+2 slashing plus 1d6 fire"


def test_damage_list_expand():
    splash = Damage("fire", 0, 0, 1, splash=True)
    assert (Damage("slashing", 1, 6, deadly=8) + splash).expand() == {
        0: [splash],
        1: [Damage("slashing", 1, 6), splash],
        2: [Damage("slashing", 1, 6, 0, 2), Damage("slashing", 1, 8), splash],
    }


def test_damage_list_basic_save():
    actual = Damage("fire", 2, 6, basic_save=True) + Damage(
        "fire", 0, 0, 1, basic_save=True
    )
    assert actual == [Damage("fire", 2, 6, 1, basic_save=True)]
    assert actual.basic_save is True


def test_expanded_damage_init():
    e = ExpandedDamage()
    assert e == {}

    e = ExpandedDamage({1: [Damage("fire", 1, 6)]})
    assert all(isinstance(k, DoS) for k in e)
    assert e == {1: [Damage("fire", 1, 6)]}

    e = ExpandedDamage(Damage("fire", 1, 6))
    assert e == {1: [Damage("fire", 1, 6)], 2: [Damage("fire", 1, 6, 0, 2)]}

    e = ExpandedDamage(Damage("slashing", 1, 4) + Damage("fire", 1, 6))
    assert e == {
        1: [Damage("slashing", 1, 4), Damage("fire", 1, 6)],
        2: [Damage("slashing", 1, 4, 0, 2), Damage("fire", 1, 6, 0, 2)],
    }

    e = ExpandedDamage([Damage("slashing", 1, 4), Damage("fire", 1, 6)])
    assert e == {
        1: [Damage("slashing", 1, 4), Damage("fire", 1, 6)],
        2: [Damage("slashing", 1, 4, 0, 2), Damage("fire", 1, 6, 0, 2)],
    }


def test_damage_plus_expanded():
    assert Damage("fire", 1, 6, 4) + {
        0: [Damage("fire", 0, 0, 4)],
        1: [Damage("fire", 0, 0, 4)],
    } == {
        0: [Damage("fire", 0, 0, 4)],
        1: [Damage("fire", 1, 6, 8)],  # simplified
        2: [Damage("fire", 1, 6, 4, 2)],
    }


def test_damage_list_plus_expanded():
    dl = Damage("fire", 1, 6) + Damage("fire", 0, 0, 1, splash=True)
    ed = {2: [Damage("fire", 1, 4, persistent=True)]}
    assert dl + ed == {
        0: [Damage("fire", 0, 0, 1, splash=True)],
        1: [Damage("fire", 1, 6), Damage("fire", 0, 0, 1, splash=True)],
        2: [
            Damage("fire", 1, 6, 0, 2),
            Damage("fire", 1, 4, persistent=True),
            Damage("fire", 0, 0, 1, splash=True),
        ],
    }


def test_expanded_damage_plus():
    e = ExpandedDamage({0: [Damage("fire", 1, 6)]})
    assert e + Damage("slashing", 2, 6, basic_save=True) == {
        -1: [Damage("slashing", 2, 6, 0, 2)],
        0: [Damage("fire", 1, 6), Damage("slashing", 2, 6)],
        1: [Damage("slashing", 2, 6, 0, 0.5)],
    }


def test_expanded_damage_sum():
    assert ExpandedDamage.sum(
        [
            {0: [Damage("fire", 1, 6)]},
            {0: [Damage("fire", 0, 0, 1)]},
        ]
    ) == {0: [Damage("fire", 1, 6, 1)]}


def test_expanded_damage_str():
    d = (Damage("fire", 1, 6) + Damage("fire", 0, 0, 1, splash=True)).expand()
    expect = """
    **Failure:** 1 fire splash
    **Success:** 1d6 fire plus 1 fire splash
    **Critical success:** (1d6)x2 fire plus 1 fire splash
    """
    assert str(d) == dedent(expect).strip()
