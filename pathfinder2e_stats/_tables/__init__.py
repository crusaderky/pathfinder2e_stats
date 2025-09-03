from __future__ import annotations

import importlib
from collections.abc import Iterator
from functools import cached_property
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats._tables.SIMPLE_PC import simple_pc

ROOT_DIR = Path(__file__).parent


def _ensure_var_dtypes(ds: Dataset) -> None:
    for k, var in ds.variables.items():
        if var.dtype == object:
            ds[k] = var.astype("U")
        else:
            assert var.dtype.kind in ("i", "b"), var


class SubTables:
    def __iter__(self) -> Iterator[str]:
        return (k for k in dir(self) if not k.startswith("_"))

    def __repr__(self) -> str:
        msg = "Available tables:"
        for k in self:
            msg += f"\n- {k}"
        return msg

    def _repr_html_(self) -> str:
        msg = "Available tables:<br>\n"
        msg += "<ul>\n"
        for k in self:
            msg += f"  <li>{k}</li>\n"
        msg += "</ul>"
        return msg


class PCTables(SubTables):
    # Hints for static type checkers
    ability_bonus: xarray.Dataset
    attack_item_bonus: xarray.Dataset
    class_proficiency: xarray.Dataset
    polymorph_attack: xarray.Dataset
    rage: xarray.Dataset
    skill_item_bonus: xarray.Dataset
    skill_proficiency: xarray.Dataset
    spell_proficiency: xarray.Dataset
    untamed_druid_attack: xarray.Dataset
    weapon_dice: xarray.Dataset
    weapon_proficiency: xarray.Dataset
    weapon_specialization: xarray.Dataset

    def __init__(self) -> None:
        fnames = sorted((ROOT_DIR / "PC").glob("*.csv"))
        assert fnames

        for fname in fnames:
            if fname.name == "_templates.csv":
                continue
            df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
            ds = df.to_xarray()
            _ensure_var_dtypes(ds)
            name = fname.name.removesuffix(".csv")

            # Bespoke tweaks
            try:
                mod = importlib.import_module(f"pathfinder2e_stats._tables.PC.{name}")
            except ModuleNotFoundError:
                pass
            else:
                try:
                    ds = mod.postproc(ds)
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError(f"Error postprocessing {fname}") from exc

            self.__dict__[name] = ds

    @property
    def level(self) -> xarray.DataArray:
        """Level of the character, as a DataArray."""
        return next(iter(self.__dict__.values())).level


class SimplePCTables(SubTables):
    @cached_property
    def weapon_attack_bonus(self) -> xarray.Dataset:
        return simple_pc.weapon_bonus(tables.PC)

    @cached_property
    def spell_attack_bonus(self) -> xarray.Dataset:
        return simple_pc.spell_bonus(tables.PC, as_DC=False)

    @cached_property
    def spell_DC(self) -> xarray.Dataset:
        return simple_pc.spell_bonus(tables.PC, as_DC=True)

    @cached_property
    def class_DC(self) -> xarray.Dataset:
        return simple_pc.class_DC(tables.PC)

    @cached_property
    def area_fire_DC(self) -> xarray.Dataset:
        return simple_pc.area_fire_DC(tables.PC)

    @cached_property
    def impulse_attack_bonus(self) -> xarray.Dataset:
        return simple_pc.impulse_bonus(tables.PC, as_DC=False)

    @cached_property
    def impulse_DC(self) -> xarray.Dataset:
        return simple_pc.impulse_bonus(tables.PC, as_DC=True)


def _read_NPC_table(fname: Path) -> DataArray:
    df = pd.read_csv(
        fname,
        index_col=0,
        header=[0, 1] if fname.name == "2-07-HP.csv" else 0,
    )

    arr = DataArray(df)

    dim_1 = arr.coords["dim_1"]
    if fname.name == "2-07-HP.csv":
        arr = arr.unstack("dim_1", fill_value=1337)
        # Undo alphabetical sorting
        arr = arr.sel(challenge=["High", "Moderate", "Low"])
    elif "High" in dim_1:
        arr = arr.rename({"dim_1": "challenge"})
    elif "max" in dim_1:
        arr = arr.rename({"dim_1": "mm"})
    elif dim_1[0] == "Unlimited":
        arr = arr.rename({"dim_1": "limited"})
        arr.coords["limited"] = [False, True]
    else:
        raise AssertionError("unreachable")  # pragma: nocover

    if "mm" in arr.dims:
        mean = arr.sum("mm").expand_dims(mm=["mean"]) / 2
        mean = mean.round(0).astype(int)
        arr = xarray.concat([arr, mean], dim="mm")

    return arr


class Tables:
    @cached_property
    def PC(self) -> PCTables:
        return PCTables()

    @cached_property
    def SIMPLE_PC(self) -> SimplePCTables:
        return SimplePCTables()

    @cached_property
    def NPC(self) -> Dataset:
        names = []
        vars = []
        fnames = sorted((ROOT_DIR / "NPC").glob("*.csv"))
        assert fnames

        for fname in fnames:
            names.append(fname.name.removesuffix(".csv").split("-")[-1])
            vars.append(_read_NPC_table(fname))

        vars = list(xarray.align(*vars, join="outer", fill_value=0))

        ds = Dataset(data_vars=dict(zip(names, vars, strict=True)))
        _ensure_var_dtypes(ds)

        # Restore priority order after align
        ds = ds.sortby(
            DataArray(
                ["Extreme", "High", "Moderate", "Low", "Terrible"],
                dims=["challenge"],
            )
        )

        ds["recall_knowledge"] = self._earn_income.DC.sel(level=ds.level) + DataArray(
            [0, 2, 5, 10],
            dims=["rarity"],
            coords={"rarity": ["Common", "Uncommon", "Rare", "Unique"]},
        )

        return ds

    @cached_property
    def SIMPLE_NPC(self) -> Dataset:
        # Level -2 weak henchman; all stats Low/min/Common
        # Matched level opponent; all stats Moderate/mean/Common
        # Level +2 boss; all stats High/max/Uncommon
        a = xarray.concat(
            [
                (
                    self.NPC.sel(challenge=challenge, mm=mm, rarity=rarity, drop=True)
                    .shift(level=level, fill_value=0)
                    .expand_dims(challenge=[new_challenge])
                )
                for (new_challenge, challenge, mm, rarity, level) in [
                    ("Weak", "Low", "min", "Common", 2),
                    ("Matched", "Moderate", "mean", "Common", 0),
                    ("Boss", "High", "max", "Uncommon", -2),
                ]
            ],
            dim="challenge",
        )
        return a.sel(level=range(1, 21)).transpose("level", "challenge", "limited")

    @cached_property
    def _earn_income(self) -> Dataset:
        """Earn income table, with extra DCs for levels -1 and 22~25."""
        fname = ROOT_DIR / "earn_income.csv"
        df = pd.read_csv(fname, index_col=0)
        ds = Dataset({"DC": df["DC"], "pathfinder": df.iloc[:, 1:]})
        ds["starfinder"] = (
            cast(DataArray, np.ceil(ds["pathfinder"] * 10)).fillna(0).astype(int)
        )
        ds = ds.rename({"dim_1": "proficiency"})
        ds["proficiency"] = ds.proficiency.astype("U")
        return ds

    @cached_property
    def DC(self) -> Dataset:
        from pathfinder2e_stats.tools import rank2level  # noqa: PLC0415

        simple_df = pd.read_csv(ROOT_DIR / "simple_DCs.csv", index_col=0)["DC"]
        adjust_df = pd.read_csv(ROOT_DIR / "DC_adjustments.csv")
        rank = DataArray(np.arange(1, 11), dims=["rank"])
        dc_by_level = self._earn_income.DC.sel(level=slice(0, None))
        return Dataset(
            coords={"rank": rank},
            data_vars={
                "simple": DataArray(simple_df),
                "by_level": dc_by_level,
                "by_rank": dc_by_level.sel(level=rank2level(rank) - 1).drop_vars(
                    "level"
                ),
                "difficulty_adjustment": DataArray(
                    adjust_df[["difficulty", "adjustment"]].set_index("difficulty")[
                        "adjustment"
                    ]
                ),
                "rarity_adjustment": DataArray(
                    adjust_df.loc[
                        ~pd.isna(adjust_df["rarity"]), ["rarity", "adjustment"]
                    ].set_index("rarity")["adjustment"]
                ),
            },
        )

    @cached_property
    def EARN_INCOME(self) -> Dataset:
        return self._earn_income.sel(level=slice(0, 21))


tables = Tables()
