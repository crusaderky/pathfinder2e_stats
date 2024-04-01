from __future__ import annotations

from collections.abc import Hashable

import numpy as np
import xarray


@xarray.register_dataarray_accessor("value_counts")
class ValueCountsAccessor:
    """Add .value_counts(dim) method to DataArray.

    Return the count of unique values for every point along dim, individually for each
    other dimension. This is conceptually the same as calling
    :meth:`pandas.Series.value_counts` individually for every series of a
    :class:`pandas.DataFrame` and then merging the output.

    **Note:**
    dask is not supported because da.unique() doesn't support the axis= parameter
    """

    _obj: xarray.DataArray

    def __init__(self, obj: xarray.DataArray):
        self._obj = obj

    def __call__(
        self, dim: Hashable, *, new_dim: Hashable = "unique_value"
    ) -> xarray.DataArray:
        def _unique(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            values, counts = np.unique(a, axis=-1, return_counts=True)
            counts = np.broadcast_to(counts, values.shape)
            return values, counts

        values, counts = xarray.apply_ufunc(
            _unique,
            self._obj,
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
        out.attrs.update(self._obj.attrs)
        return out
