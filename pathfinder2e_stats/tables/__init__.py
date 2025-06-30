from __future__ import annotations

import importlib
from collections.abc import Iterator, Mapping
from pathlib import Path

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
    def _lazy_init(self) -> None:
        if self.__dict__:
            return

        fnames = (Path(__file__).parent / "_PC").glob("*.csv")
        for fname in sorted(fnames):
            df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
            ds = df.to_xarray()
            _ensure_var_dtypes(ds)
            name = fname.name.removesuffix(".csv")

            # Bespoke tweaks
            try:
                mod = importlib.import_module(f"pathfinder2e_stats.tables._PC.{name}")
            except ModuleNotFoundError:
                pass
            else:
                mod.postproc(ds)
            self.__dict__[name] = ds

        self.__dict__["level"] = next(iter(self.__dict__.values())).level

    def __getattr__(self, key: str) -> Dataset:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"no table {key!r}") from None

    def __getitem__(self, key: str) -> Dataset:
        self._lazy_init()
        return self.__dict__[key]

    def __iter__(self) -> Iterator[str]:
        self._lazy_init()
        return iter(self.__dict__)

    def __len__(self) -> int:
        self._lazy_init()
        return len(self.__dict__)

    def __repr__(self) -> str:
        self._lazy_init()
        msg = "Available tables:"
        for k in self:
            msg += f"\n- {k}"
        return msg


def _read_NPC_table(fname: Path) -> DataArray:
    df = pd.read_csv(
        fname,
        index_col=0,
        header=[0, 1] if fname.name == "HP.csv" else 0,
    )

    arr = DataArray(df)

    dim_1 = arr.coords["dim_1"]
    if fname.name == "HP.csv":
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


def _read_NPC_tables() -> Dataset:
    names = []
    vars = []
    fnames = (Path(__file__).parent / "_NPC").glob("*.csv")

    for fname in sorted(fnames):
        names.append(fname.name.removesuffix(".csv"))
        vars.append(_read_NPC_table(fname))

    vars = list(xarray.align(*vars, join="outer", fill_value=0))

    ds = Dataset(data_vars=dict(zip(names, vars, strict=True)))
    _ensure_var_dtypes(ds)
    # Restore priority order after align
    return ds.sortby(
        DataArray(
            ["Extreme", "High", "Moderate", "Low", "Terrible"],
            dims=["challenge"],
        )
    )


def _read_earn_income_table() -> Dataset:
    fname = Path(__file__).parent / "earn_income.csv"
    df = pd.read_csv(fname, index_col=0)
    ds = Dataset({"DC": df["DC"], "income_earned": df.iloc[:, 1:]})
    ds = ds.rename({"dim_1": "proficiency"})
    ds.coords["proficiency"] = ds.proficiency.astype("U")
    return ds


PC = PCTables()
NPC = _read_NPC_tables()

EARN_INCOME = _read_earn_income_table()
# Earn income goes from level 0 to 21.
# Monsters go from -1 to 24.
# Level-based DCs go from 0 to 25.
NPC["recall_knowledge"] = EARN_INCOME.DC
DC = EARN_INCOME.DC.sel(level=(EARN_INCOME.level >= 0))
EARN_INCOME = EARN_INCOME.sel(level=(EARN_INCOME.level >= 0) & (EARN_INCOME.level < 22))

# Level -2 henchman, everything is Low
# At-level opponent, everything is Moderate
# Level +2 boss, everything is High
SIMPLE_NPC = (
    xarray.concat(
        [
            NPC.sel(challenge="Low").shift({"level": 2}, fill_value=0),
            NPC.sel(challenge="Moderate"),
            NPC.sel(challenge="High").shift({"level": -2}, fill_value=0),
        ],
        dim="challenge",
    )
    .sel(level=range(1, 21), mm="mean", drop=True)
    .transpose("level", "challenge", "limited")
)


__all__ = ("DC", "EARN_INCOME", "NPC", "PC", "SIMPLE_NPC")
