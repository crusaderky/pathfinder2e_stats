from pathfinder2e_stats import roll, tables


def test_PC():
    ds = tables.PC
    assert ds.data_vars
    for k, v in ds.variables.items():
        if k in ds.data_vars or k == "level":
            assert v.dtype.kind == "i", v
        else:
            assert v.dtype.kind == "U", v

    # test ffill
    assert ds["weapon_proficiency"].sel(level=6, weapon_proficiency_col="Fighter") == 6
    # test fill with zeros
    assert ds["attack_item_bonus"].sel(level=1, attack_item_bonus_col="Bomb") == 0


def test_NPC():
    ds = tables.NPC
    assert set(ds.dims) == {"level", "challenge", "mm", "limited"}

    assert ds.data_vars
    for v in ds.data_vars.values():
        if v.dtype.kind == "U":
            # Test that text is a well-formed dice expression, e.g. 2d6+1
            for dice in v.values.flat:
                if dice != "0":  # Fill-in for terrible
                    roll(dice)  # TODO separate pareser from roller
        else:
            assert v.dtype.kind == "i"
            if "mm" in v.dims:
                assert (v.sel(mm="max") >= v.sel(mm="min")).all()

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
