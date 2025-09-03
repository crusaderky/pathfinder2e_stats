import xarray

from ._common import postproc_classes


def postproc(ds: xarray.Dataset) -> xarray.Dataset:
    return postproc_classes(ds, extra_columns=("kineticist_dedication",))
