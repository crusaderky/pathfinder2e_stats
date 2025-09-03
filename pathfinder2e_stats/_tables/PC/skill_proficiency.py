import xarray


def postproc(ds: xarray.Dataset) -> xarray.Dataset:
    vars = []
    for k, start, stop in (
        ("rogue", 1, 6),
        ("others", 1, 3),
        ("spellcaster_dedication", 2, 3),
    ):
        v = xarray.concat(
            [ds[f"{k}/{i}"] for i in range(start, stop + 1)], dim="priority"
        ).T
        v.coords["priority"] = range(start, stop + 1)
        vars.append(v)

    vars = list(xarray.align(*vars, join="outer", fill_value=0))
    vars[2].loc[{"priority": 1}] = vars[1].sel(priority=1)

    for k in list(ds.data_vars):
        del ds[k]
    ds["envoy"] = vars[0]
    ds["rogue"] = vars[0]
    ds["others"] = vars[1]
    ds["spellcaster_dedication"] = vars[2]
    return ds
