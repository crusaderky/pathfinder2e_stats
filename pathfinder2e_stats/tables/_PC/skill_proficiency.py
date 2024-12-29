from __future__ import annotations

import xarray
from xarray import Dataset


def postproc(ds: Dataset) -> None:
    vars = {}
    for k, start, stop in (
        ("rogue", 1, 6),
        ("spellcaster_dedication", 2, 3),
        ("others", 1, 3),
    ):
        vars[k] = xarray.concat(
            [ds[f"{k}/{i}"] for i in range(start, stop + 1)], dim="priority"
        ).T
        vars[k].coords["priority"] = range(start, stop + 1)

    aligned = xarray.align(*vars.values(), join="outer", fill_value=0)
    vars = dict(zip(vars, aligned, strict=True))
    vars["spellcaster_dedication"].loc[{"priority": 1}] = vars["others"].sel(priority=1)

    for k in list(ds.data_vars):
        del ds[k]
    for k, v in vars.items():
        ds[k] = v
