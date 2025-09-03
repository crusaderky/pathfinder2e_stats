from collections.abc import Hashable

import xarray


def postproc(ds: xarray.Dataset) -> xarray.Dataset:
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

    # Sort alphabetically, except bloodrager sub-variables
    def key(kv: tuple[Hashable, xarray.DataArray]) -> tuple[str, int]:
        parts = str(kv[0]).split("_")
        if parts[0] == "bloodrager":
            return parts[0], {"weapon": 0, "bleed": 1, "spells": 2}[parts[1]]
        return parts[0], 0

    data_vars = dict(sorted(ds.data_vars.items(), key=key))
    for k, v in data_vars.items():
        del ds[k]
        ds[k] = v
    return ds
