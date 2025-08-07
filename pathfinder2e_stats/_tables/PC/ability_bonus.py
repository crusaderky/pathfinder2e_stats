import xarray


def postproc(ds: xarray.Dataset) -> None:
    vars = []
    for i in [4, 3, 2, 1]:
        vars.append(ds[f"boosts/{i}"])
        del ds[f"boosts/{i}"]
    apex = ds["apex"]
    del ds["apex"]

    ds["boosts"] = xarray.concat(vars, dim="initial").T
    ds["initial"] = [4, 3, 2, 1]
    ds["apex"] = apex
