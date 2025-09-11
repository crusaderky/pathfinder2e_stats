from __future__ import annotations

from textwrap import dedent

import pytest

from pathfinder2e_stats import Damage, DoS, ExpandedDamage


def test_damage_type_validation():
    with pytest.raises(TypeError, match="type"):
        Damage(1, 6, 4)
    with pytest.raises(TypeError, match="dice"):
        Damage("fire", True, 6)
    with pytest.raises(TypeError, match="splash"):
        Damage("fire", 1, 6, splash=1)

    Damage("fire", 1, 6, multiplier=0.5)
    Damage("fire", 1, 6, multiplier=2)
    with pytest.raises(TypeError, match="multiplier"):
        Damage("fire", 1, 6, multiplier=True)
    with pytest.raises(ValueError, match="multiplier"):
        Damage("fire", 1, 6, multiplier=3)

    for i in (2, 4, 6, 8, 10, 12):
        Damage("fire", 1, i)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 3)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 1)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 14)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 20)
    with pytest.raises(TypeError, match="faces"):
        Damage("fire", 1, "2")
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 6, two_hands=20)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 6, deadly=20)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 6, fatal=20)
    with pytest.raises(ValueError, match="faces"):
        Damage("fire", 1, 6, fatal_aim=20)

    with pytest.raises(ValueError, match=r"persistent.*splash"):
        Damage("fire", 0, 0, 1, persistent=True, splash=True)
    with pytest.raises(ValueError, match=r"persistent.*scatter"):
        Damage("fire", 0, 0, 1, persistent=True, scatter=True)
    with pytest.raises(ValueError, match=r"splash.*scatter"):
        Damage("fire", 0, 0, 1, splash=True, scatter=True)

    Damage("fire", 0, 0, 1)
    with pytest.raises(ValueError, match="dice and faces"):
        Damage("fire", 1, 0, 1)
    with pytest.raises(ValueError, match="dice and faces"):
        Damage("fire", 0, 2, 1)
    with pytest.raises(ValueError, match="dice"):
        Damage("fire", -1, 6)


def test_damage_repr():
    d = Damage("fire", 1, 6)
    assert str(d) == "**Damage** 1d6 fire"
    assert repr(d) == str(d)  # ipython calls repr()
    assert (
        d._repr_html_() == "<b>Damage</b> 1d6 fire"
    )  # jupyter calls _repr_html_ if available

    d = Damage("fire", 2, 6, 3)
    assert str(d) == "**Damage** 2d6+3 fire"

    d = Damage("fire", 2, 6, -1)
    assert str(d) == "**Damage** 2d6-1 fire"

    d = Damage("fire", 0, 0, 1)
    assert str(d) == "**Damage** 1 fire"

    d = Damage("fire", 6, 6, 1, 2)
    assert str(d) == "**Damage** (6d6+1)x2 fire"

    d = Damage("fire", 6, 6, 1, 0.5)
    assert str(d) == "**Damage** (6d6+1)/2 fire"

    d = Damage("fire", 0, 0, 1, persistent=True)
    assert str(d) == "**Damage** 1 persistent fire"

    d = Damage("fire", 0, 0, 1, splash=True)
    assert str(d) == "**Damage** 1 fire splash"

    d = Damage("piercing", 2, 6, 4, deadly=8)
    assert str(d) == "**Damage** 2d6+4 piercing deadly d8"

    d = Damage("piercing", 2, 6, 4, fatal=10)
    assert str(d) == "**Damage** 2d6+4 piercing fatal d10"

    d = Damage("piercing", 1, 8, fatal_aim=12)
    assert str(d) == "**Damage** 1d8 piercing fatal aim d12"

    d = Damage("fire", 6, 6, basic_save=True)
    assert str(d) == "**Damage** 6d6 fire, with a basic saving throw"

    d = Damage("slashing", 1, 8, two_hands=12)
    assert str(d) == "**Damage** 1d8 slashing two-hands d12"

    d = Damage("slashing", 1, 8, boost=10)
    assert str(d) == "**Damage** 1d8 slashing boost d10"

    d = Damage("piercing", 2, 8, scatter=True)
    assert str(d) == "**Damage** 2d8 piercing scatter"


def test_damage_type_copy():
    d = Damage("fire", 1, 6, 3, persistent=True)
    d2 = d.copy(multiplier=2)
    assert d2 == Damage("fire", 1, 6, 3, 2, persistent=True)
    d3 = d.copy(bonus=5)
    assert d3 == Damage("fire", 1, 6, 5, persistent=True)


def test_simplify():
    assert Damage.simplify(
        [
            Damage("piercing", 1, 6),
            Damage("piercing", 1, 6, scatter=True),
            Damage("fire", 0, 0, 1, splash=True),
            Damage("fire", 1, 4, persistent=True),
            Damage("piercing", 0, 0, 1),
            Damage("piercing", 2, 6, 2),
            Damage("piercing", 1, 8),
            Damage("piercing", 1, 8, multiplier=2),
            Damage("force", 1, 6, -6),
        ]
    ) == [
        Damage("piercing", 1, 8, multiplier=2),
        Damage("piercing", 1, 8),
        Damage("piercing", 3, 6, 2),
        Damage("piercing", 1, 6, 1, scatter=True),
        # If the combined penalties on an attack would reduce the
        # damage to 0 or below, you still deal 1 damage.
        Damage("force", 1, 6, -6),
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
        # Halving can't reduce damage below 1
        1: [Damage("fire", 0, 0, 1)],
    }
    assert Damage("fire", 0, 0, 5, basic_save=True).expand() == {
        -1: [Damage("fire", 0, 0, 10)],
        0: [Damage("fire", 0, 0, 5)],
        1: [Damage("fire", 0, 0, 2)],
    }


def test_expand_splash():
    d = Damage("fire", 1, 6, 2, splash=True)
    # Only the primary target takes damage on a miss
    assert d.expand() == {0: [d.copy(splash=False)], 1: [d], 2: [d]}


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
    """Probably possible through some class features or feats"""
    assert Damage("slashing", 2, 8, 4, deadly=8, fatal=12).expand() == {
        1: [Damage("slashing", 2, 8, 4)],
        2: [
            Damage("slashing", 2, 12, 4, 2),
            Damage("slashing", 1, 12),
            Damage("slashing", 1, 8),
        ],
    }


def test_area_fire():
    # Damage.area_fire()
    d1 = Damage("slashing", 1, 8, 4)
    e1 = Damage("slashing", 1, 8, 4, basic_save=True)
    assert d1.area_fire() == e1

    # DamageList.area_fire()
    d2 = d1 + Damage("fire", 1, 6)
    e2 = e1 + Damage("fire", 1, 6, basic_save=True)
    assert d2.area_fire() == e2

    # ExpandedDamage.area_fire()
    assert d2.expand().area_fire() == {
        -1: [Damage("slashing", 1, 8, 4, 2), Damage("fire", 1, 6, 0, 2)],
        0: [Damage("slashing", 1, 8, 4), Damage("fire", 1, 6)],
        1: [Damage("slashing", 1, 8, 4, 0.5), Damage("fire", 1, 6, 0, 0.5)],
    }

    with pytest.raises(ValueError, match="basic saving throw"):
        e1.area_fire()

    # Effects on a miss are discarded
    d = Damage("slashing", 1, 8, 4) + {0: [Damage("slashing", 0, 0, 4)]}
    assert d.area_fire() == Damage("slashing", 1, 8, 4, basic_save=True).expand()


def test_deadly_area_fire():
    """Area Fire with a Deadly weapon"""
    assert Damage("slashing", 1, 6, 4, deadly=8).area_fire().expand() == {
        1: [Damage("slashing", 1, 6, 4, 0.5)],
        0: [Damage("slashing", 1, 6, 4)],
        -1: [Damage("slashing", 1, 6, 4, 2), Damage("slashing", 1, 8)],
    }


def test_fatal_area_fire():
    """Area Fire with a Fatal weapon"""
    assert Damage("slashing", 1, 6, 4, fatal=10).area_fire().expand() == {
        1: [Damage("slashing", 1, 6, 4, 0.5)],
        0: [Damage("slashing", 1, 6, 4)],
        -1: [Damage("slashing", 1, 10, 4, 2), Damage("slashing", 1, 10)],
    }


def test_vicious_swing():
    """Vicious Swing (Fighter feat) adds 1 or more dice of damage, which
    are enlarged by fatal but don't cause deadly to bump up
    """
    assert Damage("slashing", 2, 8).vicious_swing(1) == Damage("slashing", 3, 8)

    # vicious swing die is enlarged by fatal
    assert Damage("slashing", 2, 8, fatal=12).vicious_swing(1) == Damage(
        "slashing", 3, 8, fatal=12
    )

    # vicious swing die adds to scatter damage
    assert Damage("slashing", 2, 6, scatter=True).vicious_swing(1) == Damage(
        "slashing", 3, 6, scatter=True
    )

    # 3d6 deadly d8 adds 2d8 on a crit
    # 2d6 deadly d8 with vicious swing adds 1d8 on a crit
    assert Damage("slashing", 2, 6, deadly=8).vicious_swing(1) == {
        1: [Damage("slashing", 3, 6)],
        2: [Damage("slashing", 3, 6, 0, 2), Damage("slashing", 1, 8)],
    }

    # Deadly, fatal, and scatter
    d = Damage("slashing", 2, 6, fatal=10, deadly=8, scatter=True)
    assert d.vicious_swing(3) == {
        1: [
            Damage("slashing", 5, 6),
            Damage("slashing", 0, 0, 5, splash=True),  # Scatter is affected
        ],
        2: [
            Damage("slashing", 5, 10, 0, 2),  # Fatal is affected
            Damage("slashing", 1, 10),
            Damage("slashing", 1, 8),  # Deadly not affected
            Damage("slashing", 0, 0, 6, splash=True),  # Scatter is affected
        ],
    }


def test_damage_list():
    d = Damage("slashing", 1, 6, 2) + Damage("slashing", 0, 0, 3)
    assert d == [Damage("slashing", 1, 6, 5)]
    assert str(d) == "**Damage** 1d6+5 slashing"
    assert repr(d) == str(d)  # ipython calls repr()
    # jupyter calls _repr_html_ if available
    assert d._repr_html_() == "<b>Damage</b> 1d6+5 slashing"

    d = Damage("slashing", 1, 6, 2) + Damage("fire", 1, 6)
    assert d == [Damage("slashing", 1, 6, 2), Damage("fire", 1, 6)]
    assert str(d) == "**Damage** 1d6+2 slashing plus 1d6 fire"
    assert repr(d) == str(d)
    assert d._repr_html_() == "<b>Damage</b> 1d6+2 slashing plus 1d6 fire"


def test_damage_list_expand():
    splash = Damage("fire", 0, 0, 1, splash=True)
    assert (Damage("slashing", 1, 6, deadly=8) + splash).expand() == {
        0: [splash.copy(splash=False)],  # No damage to secondary targets
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


def test_expanded_damage_init_filter_empty():
    actual = ExpandedDamage({-1: [], 0: [], 1: [Damage("fire", 1, 6)], 2: []})
    assert actual == {1: [Damage("fire", 1, 6)]}


def test_expanded_damage_expand():
    e = Damage("fire", 1, 8).expand()
    assert e.expand() is e


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
        0: [Damage("fire", 0, 0, 1)],  # No splash on secondary targets on a miss
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


def test_expanded_damage_repr():
    d = (Damage("fire", 1, 6) + Damage("fire", 0, 0, 1, splash=True)).expand()
    expect_txt = """
    **Critical success** (1d6)x2 fire plus 1 fire splash
    **Success** 1d6 fire plus 1 fire splash
    **Failure** 1 fire
    """
    expect_html = """
    <b>Critical success</b> (1d6)x2 fire plus 1 fire splash<br>
    <b>Success</b> 1d6 fire plus 1 fire splash<br>
    <b>Failure</b> 1 fire
    """

    assert repr(d) == str(d) == dedent(expect_txt).strip()
    assert d._repr_html_() == dedent(expect_html).strip()

    assert d.to_dict_of_str() == {
        "Critical success": "(1d6)x2 fire plus 1 fire splash",
        "Success": "1d6 fire plus 1 fire splash",
        "Failure": "1 fire",
    }


def test_expanded_damage_filter():
    d = (
        Damage("fire", 1, 6)
        + Damage("fire", 0, 0, 1, splash=True)
        + Damage("fire", 1, 4, persistent=True)
    ).expand()
    assert d.filter("direct") == {
        0: [Damage("fire", 0, 0, 1)],  # No splash on secondary targets on a miss
        1: [Damage("fire", 1, 6)],
        2: [Damage("fire", 1, 6, 0, 2)],
    }
    assert d.filter("persistent") == {
        1: [Damage("fire", 1, 4, persistent=True)],
        2: [Damage("fire", 1, 4, 0, 2, persistent=True)],
    }
    assert d.filter("splash") == {
        1: [Damage("fire", 0, 0, 1, splash=True)],
        2: [Damage("fire", 0, 0, 1, splash=True)],
    }
    for which in (("direct", "persistent"), ("persistent", "direct")):
        assert d.filter(*which) == {
            0: [Damage("fire", 0, 0, 1)],
            1: [Damage("fire", 1, 6), Damage("fire", 1, 4, persistent=True)],
            2: [
                Damage("fire", 1, 6, 0, 2),
                Damage("fire", 1, 4, 0, 2, persistent=True),
            ],
        }
    with pytest.raises(ValueError, match="misspelled"):
        d.filter("persistent", "misspelled")


def test_expanded_damage_simplify():
    s1 = {0: [Damage("fire", 1, 6, 1), Damage("fire", 0, 0, 1)]}
    s2 = ExpandedDamage(s1)
    assert s2 == s1
    s3 = s2.simplify()
    assert s3 == {0: [Damage("fire", 1, 6, 2)]}


def test_reduce_die():
    d = Damage("slashing", 1, 4, 3)
    d2 = d.reduce_die()
    assert d2 == Damage("slashing", 1, 2, 3)
    with pytest.raises(ValueError, match="faces"):
        d2.reduce_die()


def test_increase_die():
    d = Damage("slashing", 2, 10, 3)
    d2 = d.increase_die()
    assert d2 == Damage("slashing", 2, 12, 3)
    with pytest.raises(ValueError, match="faces"):
        d2.increase_die()


def test_two_hands():
    d = Damage("slashing", 1, 8, two_hands=12)

    # Defaults to 2 hands
    with pytest.warns(UserWarning, match="two hands"):
        actual = d.expand()
    assert actual == Damage("slashing", 1, 12).expand()

    # Triggers default on add
    with pytest.warns(UserWarning, match="two hands"):
        actual = d + Damage("fire", 1, 6)
    assert actual == Damage("slashing", 1, 12) + Damage("fire", 1, 6)

    assert d.hands(1) == Damage("slashing", 1, 8)
    assert d.hands(2) == Damage("slashing", 1, 12)
    with pytest.raises(ValueError, match="hands"):
        d.hands(0)
    with pytest.raises(ValueError, match="hands"):
        d.hands(3)
    with pytest.raises(ValueError, match="hands"):
        d.hands(True)
    with pytest.raises(ValueError, match=r"does not have .* two-hands"):
        Damage("slashing", 1, 8).hands(2)


def test_fatal_aim():
    d = Damage("piercing", 1, 8, fatal_aim=12)

    # Defaults to 2 hands
    with pytest.warns(UserWarning, match="two hands"):
        actual = d.expand()
    assert actual == Damage("piercing", 1, 8, fatal=12).expand()

    # Triggers default on add
    with pytest.warns(UserWarning, match="two hands"):
        actual = d + Damage("fire", 1, 6)
    assert actual == Damage("piercing", 1, 8, fatal=12) + Damage("fire", 1, 6)

    assert d.hands(1) == Damage("piercing", 1, 8)
    assert d.hands(2) == Damage("piercing", 1, 8, fatal=12)
    with pytest.raises(ValueError, match="hands"):
        d.hands(0)
    with pytest.raises(ValueError, match="hands"):
        d.hands(3)
    with pytest.raises(ValueError, match="hands"):
        d.hands(True)
    with pytest.raises(ValueError, match="both fatal and fatal aim"):
        Damage("piercing", 1, 8, fatal=12, fatal_aim=12)


def test_boost():
    d = Damage("fire", 1, 8, 4, boost=10)

    # Defaults to False
    with pytest.warns(UserWarning, match="boost"):
        actual = d.expand()
    assert actual == Damage("fire", 1, 8, 4).expand()

    # Triggers default on add
    with pytest.warns(UserWarning, match="boost"):
        actual = d + Damage("cold", 1, 6)
    assert actual == Damage("fire", 1, 8, 4) + Damage("cold", 1, 6)

    # Bonus damage is not replicated by boost
    # Boost damage is not doubled on a critical hit
    assert d.apply_boost(False) == Damage("fire", 1, 8, 4)
    assert d.apply_boost(True) == Damage("fire", 1, 8, 4) + {
        DoS.critical_success: [Damage("fire", 1, 10)],
        DoS.success: [Damage("fire", 1, 10)],
    }

    with pytest.raises(ValueError, match=r"does not have .* boost"):
        Damage("fire", 1, 8).apply_boost(True)

    # Deadly and fatal are not replicated
    d = Damage("fire", 4, 8, 4, boost=10, deadly=6, fatal=12)
    assert d.apply_boost(False) == Damage("fire", 4, 8, 4, deadly=6, fatal=12)
    assert d.apply_boost(True) == Damage("fire", 4, 8, 4, deadly=6, fatal=12) + {
        DoS.critical_success: [Damage("fire", 4, 10)],
        DoS.success: [Damage("fire", 4, 10)],
    }

    # Area Fire with boost weapon
    d = Damage("fire", 3, 6, 2, boost=8, basic_save=True)
    assert d.apply_boost(True) == ExpandedDamage(
        {
            DoS.success: [
                Damage("fire", 3, 8, multiplier=0.5),
                Damage("fire", 3, 6, 2, multiplier=0.5),
            ],
            DoS.failure: [
                Damage("fire", 3, 8),
                Damage("fire", 3, 6, 2),
            ],
            DoS.critical_failure: [
                Damage("fire", 3, 6, 2, multiplier=2),
                Damage("fire", 3, 8),
            ],
        }
    )


def test_scatter():
    """Unlike regular splash damage, scatter damage does not apply on a fail"""
    d = Damage("fire", 3, 8, 4, scatter=True)
    assert d.expand() == {
        1: [
            Damage("fire", 3, 8, 4),
            Damage("fire", 0, 0, 3, splash=True),
        ],
        2: [
            Damage("fire", 3, 8, 4, multiplier=2),
            Damage("fire", 0, 0, 3, splash=True),
        ],
    }


def test_scatter_fatal():
    """Fatal dice add to the scatter damage"""
    d = Damage("fire", 3, 8, 4, fatal=12, scatter=True)
    assert d.expand() == {
        1: [
            Damage("fire", 3, 8, 4),
            Damage("fire", 0, 0, 3, splash=True),
        ],
        2: [
            Damage("fire", 3, 12, 4, multiplier=2),
            Damage("fire", 1, 12),
            Damage("fire", 0, 0, 4, splash=True),
        ],
    }


def test_scatter_deadly():
    """Deadly dice are not weapon dice and do not add to the scatter damage"""
    d = Damage("fire", 3, 8, 4, deadly=10, scatter=True)
    assert d.expand() == {
        1: [
            Damage("fire", 3, 8, 4),
            Damage("fire", 0, 0, 3, splash=True),
        ],
        2: [
            Damage("fire", 3, 8, 4, multiplier=2),
            Damage("fire", 2, 10),
            Damage("fire", 0, 0, 3, splash=True),
        ],
    }


def test_scatter_boost():
    """Boost dice are not weapon dice and do not add to the scatter damage"""
    d = Damage("fire", 3, 8, 4, boost=10, scatter=True).apply_boost(True)
    assert d.expand() == {
        1: [
            Damage("fire", 3, 10),
            Damage("fire", 3, 8, 4),
            Damage("fire", 0, 0, 3, splash=True),
        ],
        2: [
            Damage("fire", 3, 8, 4, multiplier=2),
            Damage("fire", 3, 10),
            Damage("fire", 0, 0, 3, splash=True),
        ],
    }


def test_damage_hash():
    d = [
        Damage("fire", 1, 8),
        Damage("slashing", 1, 8),
        Damage("fire", 1, 8, splash=True),
        Damage("fire", 1, 8, persistent=True),
        Damage("fire", 1, 8, scatter=True),
        Damage("fire", 1, 8, basic_save=True),
        Damage("fire", 1, 8, two_hands=12),
        Damage("fire", 1, 8, deadly=12),
        Damage("fire", 1, 8, fatal=12),
        Damage("fire", 1, 8, fatal_aim=12),
        Damage("fire", 1, 8, boost=12),
    ]
    assert len(set(d + d)) == len(d)
