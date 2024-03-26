from __future__ import annotations

from pathlib import Path

import pandas as pd
from xarray import DataArray, Dataset


def _read_raw_tables(path: str) -> Dataset:
    data_vars = {}
    fnames = (Path(__file__).parent / path).glob("*.csv")

    for fname in sorted(fnames):
        df = pd.read_csv(fname, index_col=0).ffill().fillna(0).astype(int)
        name = fname.name.removesuffix(".csv")
        data_vars[name] = DataArray(df).rename({"dim_1": name + "_col"})

    ds = Dataset(data_vars=data_vars)
    for k, coord in ds.coords.items():
        if coord.dtype == object:
            ds.coords[k] = coord.astype("U")
    return ds


raw_PC = _read_raw_tables("PC")
raw_NPC = _read_raw_tables("NPC")

__all__ = ("raw_PC", "raw_NPC")
