from __future__ import annotations

import xarray
from xarray import Dataset


def postproc(ds: Dataset) -> None:
    vars = []
    for i in [4, 3, 2, 1]:
        vars.append(ds[f"boosts/{i}"])
        del ds[f"boosts/{i}"]
    apex = ds["apex"]
    del ds["apex"]

    ds["boosts"] = xarray.concat(vars, dim="initial").T
    ds["initial"] = [4, 3, 2, 1]
    ds["apex"] = apex
