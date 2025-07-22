from __future__ import annotations

import importlib
from collections.abc import Iterator, Mapping
from functools import cached_property
from pathlib import Path
from typing import cast

import pandas as pd
import xarray
from xarray import DataArray, Dataset


def _ensure_var_dtypes(ds: Dataset) -> None:
    for k, var in ds.variables.items():
        if var.dtype == object:
            ds[k] = var.astype("U")
        else:
            assert var.dtype.kind in ("i", "b"), var


class PCTables(Mapping[str, Dataset]):
    def __init__(self) -> None:
        fnames = sorted((Path(__file__).parent / "_PC").glob("*.csv"))
        assert fnames

        for fname in fnames:
            df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
            ds = df.to_xarray()
            _ensure_var_dtypes(ds)
            name = fname.name.removesuffix(".csv")

            # Bespoke tweaks
            try:
                mod = importlib.import_module(f"pathfinder2e_stats._tables._PC.{name}")
            except ModuleNotFoundError:
                pass
            else:
                mod.postproc(ds)
            self.__dict__[name] = ds

        self.level = next(iter(self.__dict__.values())).level

    def __getitem__(self, item: str) -> Dataset:
        return self.__dict__[item]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)

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


def _read_NPC_table(fname: Path) -> DataArray:
    df = pd.read_csv(
        fname,
        index_col=0,
        header=[0, 1] if fname.name == "2-07-HP.csv" else 0,
    )

    arr = DataArray(df)

    dim_1 = arr.coords["dim_1"]
    if fname.name == "2-07-HP.csv":
        arr = arr.unstack("dim_1", fill_value=1337)  # noqa: PD010
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
    def NPC(self) -> Dataset:
        names = []
        vars = []
        fnames = sorted((Path(__file__).parent / "_NPC").glob("*.csv"))
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
    def SIMPLE_NPC(self) -> DataArray:
        # Level -2 weak henchman; all stats Low/min/Common
        # Matched level opponent; all stats Moderate/mean/Common
        # Level +2 boss; all stats High/max/Uncommon
        a = xarray.concat(
            [
                (
                    self.NPC
                    .sel(challenge=challenge, mm=mm, rarity=rarity, drop=True)
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
        return (
            a
            .sel(level=range(1, 21))
            .transpose("level", "challenge", "limited")
        )

    @cached_property
    def _earn_income(self) -> Dataset:
        """Earn income table, with extra DCs for levels -1 and 22~25."""
        fname = Path(__file__).parent / "earn_income.csv"
        df = pd.read_csv(fname, index_col=0)
        ds = Dataset({"DC": df["DC"], "income_earned": df.iloc[:, 1:]})
        ds = ds.rename({"dim_1": "proficiency"})
        ds.coords["proficiency"] = ds.proficiency.astype("U")
        return ds

    @cached_property
    def DC(self) -> DataArray:
        return self._earn_income.DC.sel(level=slice(0, None))

    @cached_property
    def EARN_INCOME(self) -> Dataset:
        return self._earn_income.sel(level=slice(0, 21))
