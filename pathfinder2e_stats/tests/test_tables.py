import pytest

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


def test_PC_inventory():
    assert set(tables.PC.__dict__) == set(PC_TABLES) | {"_inventory"}


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
    assert tables.PC.weapon_proficiency.fighter.sel(level=6, mastery=True) == 6
    # test fill with zeros
    assert tables.PC.attack_item_bonus.bomb.sel(level=1) == 0


def test_PC_postproc():
    """Test that .py post-processing scripts in the _PC directory are executed"""
    ds = tables.PC.ability_bonus
    assert tuple(ds.data_vars) == ("boosts", "apex")
    assert tuple(ds.coords) == ("level", "initial")
    assert ds.boosts.dims == ("level", "initial")


def test_PC_repr():
    s = repr(tables.PC)
    assert "- ability_bonus\n" in s


def test_PC_html_repr():
    s = tables.PC._repr_html_()
    assert "<li>ability_bonus</li>" in s


def test_PC_code_completion():
    assert "ability_bonus" in dir(tables.PC)


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


@pytest.mark.parametrize("table", ["strike_attack_bonus", "spell_attack_bonus"])
def test_SIMPLE_PC(table):
    ds = getattr(tables.SIMPLE_PC, table)
    assert ds.level[0] == 1
    assert ds.level[-1] == 20
    assert ds.data_vars
    assert "level" in ds.coords
    assert "component" in ds.coords
    for v in ds.sum("component").data_vars.values():
        assert v.min() >= 6
        assert v.max() <= 38
    assert not set(ds.coords) - {
        "level",
        "component",
        "doctrine",
        "research_field",
        "ability",
        "mastery",
    }


def test_SIMPLE_PC_repr():
    s = repr(tables.SIMPLE_PC)
    assert "- strike_attack_bonus\n" in s


def test_SIMPLE_PC_html_repr():
    s = tables.SIMPLE_PC._repr_html_()
    assert "<li>strike_attack_bonus</li>" in s


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
    assert ds.sel(level=7).income_earned.values.tolist() == [0.4, 2, 2.5, 2.5, 2.5]
    assert ds.DC.dtype.kind == "i"
    assert ds.income_earned.dtype.kind == "f"
    assert ds.proficiency.dtype.kind == "U"
