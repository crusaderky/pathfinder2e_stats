import xarray

from .common import postproc_classes


def postproc(ds: xarray.Dataset) -> None:
    postproc_classes(ds)
