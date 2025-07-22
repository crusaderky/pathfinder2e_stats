import xarray


def postproc(ds: xarray.Dataset) -> None:
    vars = {}
    for cls in ("fighter", "gunslinger"):
        vars[cls] = xarray.concat(
            [ds[f"{cls}/{mastery}"] for mastery in ("mastery", "other")],
            dim="mastery",
        ).T
        del ds[f"{cls}/mastery"]
        del ds[f"{cls}/other"]
    ds["mastery"] = [True, False]

    for cls in list(ds.data_vars):
        vars[cls] = ds[cls]
        del ds[cls]

    for k, v in vars.items():
        ds[k] = v
