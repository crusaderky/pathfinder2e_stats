from __future__ import annotations

from pathfinder2e_stats import Damage


def test_damage_type_str():
    d = Damage("fire", 1, 6)
    assert str(d) == "1d6 fire damage"

    d = Damage("fire", 2, 6, 3)
    assert str(d) == "2d6+3 fire damage"

    d = Damage("fire", 2, 6, -1)
    assert str(d) == "2d6-1 fire damage"

    d = Damage("fire", 0, 0, 1)
    assert str(d) == "1 fire damage"

    d = Damage("fire", 6, 6, 1, 2)
    assert str(d) == "(6d6+1)x2 fire damage"

    d = Damage("fire", 6, 6, 1, 0.5)
    assert str(d) == "(6d6+1)/2 fire damage"

    d = Damage("fire", 0, 0, 1, persistent=True)
    assert str(d) == "1 persistent fire damage"

    d = Damage("fire", 0, 0, 1, splash=True)
    assert str(d) == "1 fire splash damage"


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
