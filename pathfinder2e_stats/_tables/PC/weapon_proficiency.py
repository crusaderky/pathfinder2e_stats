import xarray

from ._common import postproc_classes


def postproc(ds: xarray.Dataset) -> None:
    postproc_classes(ds, extra_columns=("fighter_dedication", "weapon_proficiency"))
