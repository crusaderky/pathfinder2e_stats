import math

import pytest
import xarray

from pathfinder2e_stats import roll, tables

PC_TABLES = [
    "ability_bonus",
    "attack_item_bonus",
    "class_proficiency",
    "polymorph_attack",
    "rage",
    "skill_item_bonus",
    "skill_proficiency",
    "spell_proficiency",
    "untamed_druid_attack",
    "weapon_dice",
    "weapon_proficiency",
    "weapon_specialization",
]

SIMPLE_PC_TABLES = [
    "weapon_attack_bonus",
    "spell_attack_bonus",
    "spell_DC",
    "class_DC",
    "impulse_attack_bonus",
    "impulse_DC",
    "area_fire_DC",
]


@pytest.mark.parametrize("table", PC_TABLES)
def test_PC(table):
    assert table in tables.PC.__annotations__
    ds = getattr(tables.PC, table)
    assert ds.level[0] == 1
    assert ds.level[-1] == 20
    assert ds.data_vars

    for k, v in ds.variables.items():
        if k in ds.data_vars or k in ("level", "initial", "priority"):
            assert v.dtype.kind == "i", v
        elif k == "mastery":
            assert v.dtype.kind == "b", v
        else:
            assert v.dtype.kind == "U", v


def test_PC_levels():
    assert tables.PC.level[0] == 1
    assert tables.PC.level[-1] == 20
    assert tables.PC.level.coords["level"][0] == 1


def test_PC_fill():
    # test ffill
    assert tables.PC.weapon_proficiency.barbarian.sel(level=6) == 4
    # test bfill with zeros
    assert tables.PC.attack_item_bonus.bomb.sel(level=1) == 0
    # test complete fill with zeros
    assert (
        tables.PC.weapon_proficiency.operative.sel(
            level=6, mastery=False, category="advanced"
        )
        == 0
    )


def test_PC_postproc():
    """Test that .py post-processing scripts in the _PC directory are executed"""
    ds = tables.PC.ability_bonus
    assert tuple(ds.data_vars) == ("boosts", "apex")
    assert tuple(ds.coords) == ("level", "initial")
    assert ds.boosts.dims == ("level", "initial")


@pytest.mark.parametrize("table", SIMPLE_PC_TABLES)
def test_SIMPLE_PC(table):
    ds = getattr(tables.SIMPLE_PC, table)
    assert ds.level[0] == 1
    assert ds.level[-1] == 20
    assert ds.data_vars
    assert "level" in ds.coords
    assert "component" in ds.coords
    for v in ds.sum("component").data_vars.values():
        offset = 0 if table.endswith("_bonus") else 10
        # Absolute worst is a Gunslinger, untrained with
        # an Advanced non-finesse weapon
        assert v.min() >= 3 + offset
        assert v.max() <= 38 + offset
    assert not set(ds.coords) - {
        "level",
        "component",
        "doctrine",
        "research_field",
        "ability",
        "mastery",
        "category",
    }
    for dim in ("component", "doctrine", "research_field", "ability", "category"):
        if dim in ds.coords:
            assert ds[dim].dtype.kind == "U"


@pytest.mark.parametrize("table", SIMPLE_PC_TABLES)
def test_SIMPLE_PC_dims(table):
    ds = getattr(tables.SIMPLE_PC, table)
    EXTRA_DIMS = {
        ("weapon_attack_bonus", "alchemist"): ("research_field",),
        ("weapon_attack_bonus", "cleric"): ("doctrine",),
        ("weapon_attack_bonus", "fighter"): ("mastery", "category"),
        ("weapon_attack_bonus", "gunslinger"): ("mastery", "category", "ability"),
        ("weapon_attack_bonus", "operative"): ("mastery", "category"),
        ("spell_attack_bonus", "cleric"): ("doctrine",),
        ("spell_DC", "cleric"): ("doctrine",),
        ("class_DC", "cleric"): ("doctrine",),
        ("area_fire_DC", "cleric"): ("doctrine",),
    }
    for k, v in ds.data_vars.items():
        expect = ("level", "component", *EXTRA_DIMS.get((table, k), ()))
        assert v.dims == expect, (table, k, v.dims, expect)


@pytest.mark.parametrize(
    "cls,sel,expect",
    [
        ("fighter", {}, 5),
        ("gunslinger", {"ability": "DEX"}, 0),
        ("gunslinger", {"ability": "STR"}, 0),
        ("operative", {}, 0),
    ],
)
def test_SIMPLE_PC_untrained(cls, sel, expect):
    """Gunslingers and operatives are untrained in advanced weapons outside
    of their mastery. Don't add level.
    """
    ds = tables.SIMPLE_PC.weapon_attack_bonus[cls].sel(
        level=5, component="level", **sel
    )
    assert ds.sel(mastery=False, category="advanced") == expect
    assert ds.sel(mastery=True, category="advanced") == 5
    assert ds.sel(mastery=False, category="martial") == 5
    assert ds.sel(mastery=True, category="martial") == 5


def test_SIMPLE_PC_bonus_vs_offset():
    xarray.testing.assert_equal(
        tables.SIMPLE_PC.spell_attack_bonus.sum("component") + 10,
        tables.SIMPLE_PC.spell_DC.sum("component"),
    )
    # Gate attenuator means the difference is between 6 and 10
    impulse_delta = tables.SIMPLE_PC.impulse_DC.sum(
        "component"
    ) - tables.SIMPLE_PC.impulse_attack_bonus.sum("component")
    assert (impulse_delta >= 6).all()
    assert (impulse_delta <= 10).all()


def test_PC_iter():
    assert set(tables.PC.__dict__) == set(PC_TABLES)
    assert set(tables.PC) == set(PC_TABLES) | {"level"}


def test_SIMPLE_PC_iter():
    assert set(tables.SIMPLE_PC) == set(SIMPLE_PC_TABLES)


def test_PC_repr():
    s = repr(tables.PC)
    assert "- ability_bonus\n" in s


def test_PC_html_repr():
    s = tables.PC._repr_html_()
    assert "<li>ability_bonus</li>" in s


def test_SIMPLE_PC_repr():
    s = repr(tables.SIMPLE_PC)
    assert "- impulse_DC\n" in s


def test_SIMPLE_PC_html_repr():
    s = tables.SIMPLE_PC._repr_html_()
    assert "<li>impulse_DC</li>" in s


def test_NPC():
    ds = tables.NPC
    assert set(ds.dims) == {"level", "challenge", "mm", "limited", "rarity"}

    assert ds.data_vars
    for v in ds.data_vars.values():
        if v.dtype.kind == "U":
            # Test that text is a well-formed dice expression, e.g. 2d6+1
            for dice in v.values.flat:
                if dice != "0":  # Fill-in for challenge='Terrible'
                    roll(dice)  # TODO separate parser from roller
        else:
            assert v.dtype.kind == "i"
            if "mm" in v.dims:
                assert (v.sel(mm="max") >= v.sel(mm="mean")).all()
                assert (v.sel(mm="mean") >= v.sel(mm="min")).all()

    # Test that coords have not been reordered alphabetically
    assert ds.challenge.values.tolist() == [
        "Extreme",
        "High",
        "Moderate",
        "Low",
        "Terrible",
    ]

    # Test that mean uses mathematical rounding and not truncation
    assert ds.resistances.sel(level=2).values.tolist() == [5, 2, 4]

    # Test that Extreme and Terrible are filled with zeros when missing
    assert ds.HP.sel(level=2, mm="min").values.tolist() == [0, 36, 28, 21, 0]

    # Test that unstack didn't need to use fill values
    HP = ds.HP.sel(challenge=["High", "Moderate", "Low"])
    assert (HP > 0).all()
    assert (HP < 700).all()


def test_SIMPLE_NPC():
    ds = tables.SIMPLE_NPC
    assert set(ds.dims) == {"level", "challenge", "limited"}

    # Levels have been clipped to PC levels
    assert ds.level[0] == 1
    assert ds.level[-1] == 20

    # Challenge levels have been trimmed and reversed
    assert ds.challenge.values.tolist() == ["Weak", "Matched", "Boss"]

    assert ds.data_vars
    for v in ds.data_vars.values():
        # recall_knowledge has gained challenge compared to tables.NPC
        assert v.dims in (("level", "challenge"), ("level", "challenge", "limited"))

    # AC was shifted by level and challenge
    assert ds.AC.sel(level=1).values.tolist() == [12, 15, 19]
    # HP was shifted by level, challenge, and mm
    assert ds.HP.sel(level=1).values.tolist() == [5, 20, 59]
    # Recall Knowledge was shifted by level and rarity
    assert ds.recall_knowledge.sel(level=1).values.tolist() == [13, 15, 20]


def test_DC():
    for v in tables.DC.data_vars.values():
        assert v.dtype.kind == "i", v

    assert tables.DC.difficulty_adjustment.values.tolist() == [-10, -5, -2, 0, 2, 5, 10]
    assert tables.DC.rarity_adjustment.values.tolist() == [0, 2, 5, 10]
    assert tables.DC.simple.values.tolist() == [10, 15, 20, 30, 40]

    assert tables.DC.level[0] == 0
    assert tables.DC.level[-1] == 25
    assert tables.DC.by_level.coords["level"][0] == 0
    assert tables.DC.by_level.coords["level"][-1] == 25
    assert tables.DC.by_level.sel(level=5) == 20

    assert tables.DC["rank"][0] == 1
    assert tables.DC["rank"][-1] == 10
    assert tables.DC.by_rank.dims == ("rank",)
    assert tables.DC.by_rank.sel(rank=3) == 20


def test_earn_income():
    ds = tables.EARN_INCOME
    assert ds.level[0] == 0
    assert ds.level[-1] == 21
    assert ds.sel(level=7).DC == 23
    assert ds.sel(level=7).pathfinder.values.tolist() == [0.4, 2, 2.5, 2.5, 2.5]
    assert ds.DC.dtype.kind == "i"
    assert ds.pathfinder.dtype.kind == "f"
    assert ds.proficiency.dtype.kind == "U"

    # 1 Starfinder credit = 1 SP; CPs are rounded up
    assert ds.sel(level=2).starfinder.values.tolist() == [1, 3, 3, 3, 3]
    assert ds.sel(level=7).starfinder.values.tolist() == [4, 20, 25, 25, 25]
    assert ds.starfinder.dtype.kind == "i"

    # Level 21 is only for critical successes at level 20.
    # Level 21 Failed is N/A in Pathfinder and 0 in Starfinder due to dtype constraints.
    crit20 = ds.sel(level=21, proficiency="Failed")
    assert math.isnan(crit20.pathfinder)
    assert crit20.starfinder == 0
