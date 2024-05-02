from pathfinder2e_stats import tables


def test_raw_PC():
    ds = tables.raw_PC
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
