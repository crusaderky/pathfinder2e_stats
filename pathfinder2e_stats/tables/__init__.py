from __future__ import annotations

from pathlib import Path

import pandas as pd
from xarray import DataArray, Dataset, align, concat


def _ensure_var_dtypes(ds: Dataset) -> None:
    for k, var in ds.variables.items():
        if var.dtype == object:
            ds[k] = var.astype("U")
        else:
            assert var.dtype.kind in ("i", "b"), var


def _read_PC_tables() -> Dataset:
    data_vars = {}
    fnames = (Path(__file__).parent / "PC").glob("*.csv")

    for fname in sorted(fnames):
        df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
        name = fname.name.removesuffix(".csv")
        data_vars[name] = DataArray(df).rename({"dim_1": name + "_col"})

    ds = Dataset(data_vars=data_vars)
    _ensure_var_dtypes(ds)
    return ds


def _read_NPC_table(fname: Path) -> DataArray:
    df = pd.read_csv(
        fname,
        index_col=0,
        header=[0, 1] if fname.name == "HP.csv" else 0,
    )

    arr = DataArray(df)

    dim_1 = arr.coords["dim_1"]
    if fname.name == "HP.csv":
        arr = arr.unstack("dim_1")
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
        arr = concat([arr, mean], dim="mm")

    return arr


def _read_NPC_tables() -> Dataset:
    names = []
    vars = []
    fnames = (Path(__file__).parent / "NPC").glob("*.csv")

    for fname in sorted(fnames):
        names.append(fname.name.removesuffix(".csv"))
        vars.append(_read_NPC_table(fname))

    vars = list(align(*vars, join="outer", fill_value=0))

    ds = Dataset(data_vars=dict(zip(names, vars, strict=True)))
    _ensure_var_dtypes(ds)
    # Restore priority order after align
    ds = ds.sortby(
        DataArray(
            ["Extreme", "High", "Moderate", "Low", "Terrible"],
            dims=["challenge"],
        )
    )
    return ds


PC = _read_PC_tables()
NPC = _read_NPC_tables()

__all__ = ("PC", "NPC")
