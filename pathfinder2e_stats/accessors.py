from __future__ import annotations

from collections.abc import Hashable

import numpy as np
import xarray


def value_counts(
    obj: xarray.DataArray, dim: Hashable, *, new_dim: Hashable = "unique_value", normalize: bool=False
) -> xarray.DataArray:
    """Return the count of unique values for every point along dim, individually for
    each other dimension.

    This is conceptually the same as calling :meth:`pandas.Series.value_counts`
    individually for every series of a :class:`pandas.DataFrame` and then merging the
    output.

    This function can also be called as a method
    ``xarray.DataArray.value_counts(dim, new_dim="unique_value", normalize=False)``.

    :param obj:
        :class:`xarray.DataArray` to iterate upon.
    :param dim:
        Name of the dimension to count the values along.
        It will be removed in the output array.
    :param new_dim: (optional; default=``unique_value``)
        Name of the new dimension in the output array.
    :param normalize: (optional; default=False)
        Return proportions rather than frequencies.
    :returns:
        :class:`xarray.DataArray` with the same dimensions as the input array,
        minus dim, plus new_dim.
    """
    def _unique(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        values, counts = np.unique(a, axis=-1, return_counts=True)
        counts = np.broadcast_to(counts, values.shape)
        return values, counts

    values, counts = xarray.apply_ufunc(
        _unique,
        obj,
        input_core_dims=[[dim]],
        output_core_dims=[["__i"], ["__i"]],
    )
    unique_values = xarray.apply_ufunc(
        np.unique,
        values,
        input_core_dims=[values.dims],
        output_core_dims=[[new_dim]],
    )
    out = xarray.where(values == unique_values, counts, 0).sum("__i")
    out.coords[new_dim] = unique_values
    out.attrs.update(obj.attrs)
    return out / obj.sizes[dim] if normalize else out


@xarray.register_dataarray_accessor("value_counts")
class ValueCountsAccessor:
    """Add .value_counts(...) method to DataArray"""

    _obj: xarray.DataArray

    def __init__(self, obj: xarray.DataArray):
        self._obj = obj

    def __call__(
        self, dim: Hashable, *, new_dim: Hashable = "unique_value", normalize: bool=False
    ) -> xarray.DataArray:
        return value_counts(self._obj, dim, new_dim=new_dim, normalize=normalize)
