from __future__ import annotations

from collections.abc import Hashable
from itertools import groupby
from typing import Literal

import numpy as np
import pandas as pd
import xarray
from xarray import DataArray, Dataset


def value_counts(
    obj: DataArray,
    dim: Hashable,
    *,
    new_dim: Hashable = "unique_value",
    normalize: bool = False,
) -> DataArray:
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

    _obj: DataArray

    def __init__(self, obj: DataArray):
        self._obj = obj

    def __call__(
        self,
        dim: Hashable,
        *,
        new_dim: Hashable = "unique_value",
        normalize: bool = False,
    ) -> DataArray:
        return value_counts(self._obj, dim, new_dim=new_dim, normalize=normalize)


def display(
    obj: DataArray | Dataset,
    name: Hashable | None = None,
    *,
    max_rows: int = 26,
    describe: bool | Literal["auto"] = "auto",
) -> None:
    from IPython.display import display_html  # noqa: PLC0415

    if isinstance(obj, DataArray):
        if name is None:
            name = obj.name
        if name is None:
            name = "(unnamed)"
        obj = obj.to_dataset(name=name)

    # Group variables by first dimension
    def key(kv: tuple[Hashable, DataArray]) -> str:
        _, v = kv
        return str(v.dims[0]) if v.dims else ""

    for _, group in groupby(sorted(obj.data_vars.items(), key=key), key=key):
        group_vars = dict(group)

        # Unique dimensions, ordered by first seen
        dims = list(
            dict.fromkeys(dim for var in group_vars.values() for dim in var.dims)
        )
        dfs = []
        for k, v in group_vars.items():
            v = v.expand_dims("variable")
            v.coords["variable"] = [k]
            for dim in dims:
                if dim not in v.dims:
                    v = v.expand_dims(dim)
                    v.coords[dim] = [""]
            if len(v.dims) > 2:
                v = v.stack(__col=["variable", *dims[1:]])
            elif dims:
                v = v.transpose(dims[0], "variable")
            df = v.to_pandas()
            if not isinstance(df, pd.DataFrame):
                df = df.to_frame()
                df.columns.name = "variable"
                df.index = [""]
            dfs.append(df)
        df = pd.concat(dfs, axis=1)

        if (describe == "auto" and df.shape[0] > max_rows) or describe is True:
            df = df.describe()

        display_html(df.to_html(max_rows=max_rows), raw=True)


@xarray.register_dataarray_accessor("display")
@xarray.register_dataset_accessor("display")
class DisplayAccessor:
    """Add .display(...) method to DataArray and Dataset"""

    _obj: DataArray | Dataset

    def __init__(self, obj: DataArray | Dataset):
        self._obj = obj

    def __call__(
        self,
        name: str | None = None,
        *,
        max_rows: int = 26,
        describe: bool | Literal["auto"] = "auto",
    ) -> None:
        return display(self._obj, name=name, max_rows=max_rows, describe=describe)
