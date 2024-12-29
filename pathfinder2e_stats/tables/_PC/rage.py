from __future__ import annotations

import xarray
from xarray import Dataset


def postproc(ds: Dataset) -> None:
    ds["superstition"] = xarray.concat(
        [ds[f"superstition/vs={vs}"] for vs in ("spellcasters", "others")],
        dim="vs",
    ).T
    ds["vs"] = ["spellcasters", "others"]
    for vs in ("spellcasters", "others"):
        del ds[f"superstition/vs={vs}"]

    ds["bloodrager_spells"] = xarray.concat(
        [ds[f"bloodrager_spells/{drained=}"] for drained in (0, 1, 2)],
        dim="drained",
    ).T
    for drained in (0, 1, 2):
        del ds[f"bloodrager_spells/{drained=}"]

    # Sort alphabetically
    data_vars = dict(sorted(ds.data_vars.items()))
    for k in data_vars:
        del ds[k]
    for k, v in data_vars.items():
        ds[k] = v
