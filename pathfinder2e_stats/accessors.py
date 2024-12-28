from __future__ import annotations

from collections.abc import Hashable

import numpy as np
import xarray


def value_counts(
    obj: xarray.DataArray,
    dim: Hashable,
    *,
    new_dim: Hashable = "unique_value",
    normalize: bool = False,
) -> xarray.DataArray:
    """pandas-style value_counts.

    See api.rst for full documentation"""

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
        self,
        dim: Hashable,
        *,
        new_dim: Hashable = "unique_value",
        normalize: bool = False,
    ) -> xarray.DataArray:
        return value_counts(self._obj, dim, new_dim=new_dim, normalize=normalize)
