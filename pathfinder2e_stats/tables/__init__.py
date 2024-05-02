from __future__ import annotations

from pathlib import Path

import pandas as pd
from xarray import DataArray, Dataset, align


def _ensure_text_coords(ds: Dataset) -> None:
    for k, coord in ds.coords.items():
        if coord.dtype == object:
            ds.coords[k] = coord.astype("U")


def _read_raw_PC_tables() -> Dataset:
    data_vars = {}
    fnames = (Path(__file__).parent / "PC").glob("*.csv")

    for fname in sorted(fnames):
        df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
        name = fname.name.removesuffix(".csv")
        data_vars[name] = DataArray(df).rename({"dim_1": name + "_col"})

    ds = Dataset(data_vars=data_vars)
    _ensure_text_coords(ds)
    return ds


def _read_raw_NPC_table(fname: Path) -> DataArray:
    df = pd.read_csv(
        fname,
        index_col=0,
        header=[0, 1] if fname.name == "HP.csv" else 0,
    )

    dtypes = set(df.dtypes)
    assert len(dtypes) == 1
    dtype = dtypes.pop()
    if dtype == object:
        df = df.astype("U")
    else:
        assert dtype == int

    arr = DataArray(df)
    return arr


def _read_raw_NPC_tables() -> Dataset:
    names = []
    vars = []
    fnames = (Path(__file__).parent / "NPC").glob("*.csv")

    for fname in sorted(fnames):
        names.append(fname.name.removesuffix(".csv"))
        vars.append(_read_raw_NPC_table(fname))

    vars = list(align(*vars, join="outer", fill_value=0))

    ds = Dataset(data_vars=dict(zip(names, vars, strict=True)))
    _ensure_text_coords(ds)
    return ds


raw_PC = _read_raw_PC_tables()
raw_NPC = _read_raw_NPC_tables()

__all__ = ("raw_PC", "raw_NPC")
