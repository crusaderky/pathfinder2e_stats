import pytest

from pathfinder2e_stats import roll, tables


def test_PC():
    t = tables.PC

    # Test Mapping interface
    assert len(t)
    assert len(t) == len(list(t))
    k0 = next(iter(t))
    assert k0 in repr(t)
    # Items can be accessed via attribute or key
    assert t[k0] is getattr(t, k0)

    with pytest.raises(AttributeError, match="no table 'PC.nonexistent'"):
        _ = t.nonexistent
    with pytest.raises(KeyError, match="'nonexistent'"):
        _ = t["nonexistent"]

    for k, ds in t.items():
        assert ds.level[0] == 1
        assert ds.level[-1] == 20

        if k != "level":
            assert ds.data_vars
            for k, v in ds.variables.items():
                if k in ds.data_vars or k in ("level", "initial", "priority"):
                    assert v.dtype.kind == "i", v
                else:
                    assert v.dtype.kind == "U", v

    assert t.level[0] == 1
    assert t.level[-1] == 20
    assert t.level.coords["level"][0] == 1

    # test ffill
    assert t.weapon_proficiency.fighter.sel(level=6) == 6
    # test fill with zeros
    assert t.attack_item_bonus.bomb.sel(level=1) == 0


def test_PC_postproc():
    """Test that .py post-processing scripts in the _PC directory are executed"""
    ds = tables.PC.ability_bonus
    assert tuple(ds.data_vars) == ("boosts", "apex")
    assert tuple(ds.coords) == ("level", "initial")
    assert ds.boosts.dims == ("level", "initial")


def test_PC_repr():
    s = repr(tables.PC)
    assert "- ability_bonus\n" in s


def test_html_repr():
    s = tables.PC._repr_html_()
    assert "<li>ability_bonus</li>" in s


def test_NPC():
    ds = tables.NPC
    assert set(ds.dims) == {"level", "challenge", "mm", "limited"}

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

    # Test that levels have been clipped to PC levels
    assert ds.level[0] == 1
    assert ds.level[-1] == 20

    # Challenge levels have been trimmed and reversed
    assert ds.challenge.values.tolist() == [
        "Low",
        "Moderate",
        "High",
    ]

    assert ds.data_vars
    for v in ds.data_vars.values():
        # recall_knowledge has gained challenge compared to tables.NPC
        assert v.dims in (("level", "challenge"), ("level", "challenge", "limited"))

    # Test shifting
    assert ds.AC.sel(level=1).values.tolist() == [12, 15, 19]
    assert ds.recall_knowledge.sel(level=1).values.tolist() == [13, 15, 18]


def test_DC():
    assert tables.DC.level[0] == 0
    assert tables.DC.level[-1] == 25
    assert tables.DC[0] == 14
    assert tables.DC[-1] == 50
    assert tables.DC.coords["level"][0] == 0
    assert tables.DC.coords["level"][-1] == 25
    assert tables.DC.dtype.kind == "i"


def test_earn_income():
    ds = tables.EARN_INCOME
    assert ds.level[0] == 0
    assert ds.level[-1] == 21
    assert ds.sel(level=7).DC == 23
    assert ds.sel(level=7).income_earned.values.tolist() == [0.4, 2, 2.5, 2.5, 2.5]
    assert ds.DC.dtype.kind == "i"
    assert ds.income_earned.dtype.kind == "f"
    assert ds.proficiency.dtype.kind == "U"
