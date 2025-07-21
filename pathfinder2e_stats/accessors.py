"""xarray accessors for DataArray and Dataset objects.

See api.rst for full documentation.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterator
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
    """pandas-style value_counts"""

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


def _to_dataframes(
    obj: DataArray | Dataset,
    name: str | None = None,
    *,
    # This is carefully picked to be enough to fit everything from .tables
    max_rows: int = 26,
    describe: bool | Literal["auto"] = "auto",
) -> Iterator[pd.DataFrame]:
    """Convert a DataArray or Dataset to one or more easily printable pandas DataFrames,
    grouped by the first dimension of each variable.
    """
    if isinstance(obj, DataArray):
        if name is None:
            name = str(obj.name) if obj.name is not None else "(unnamed)"
            if name in obj.coords:  # Invalid
                name = "values"
        obj = obj.to_dataset(name=name)

    # Reorder dimensions, making sure that they follow the same first-seen order
    # throughout the Dataset. Move the longest dimension to the front.
    longest_dim = np.max(list(obj.sizes.values())) if obj.sizes else 0
    dims_sorted = dict(
        sorted(
            obj.sizes.items(),
            key=lambda kv: (kv[1] != longest_dim, str(kv[0])),
        )
    )
    obj = obj.transpose(*dims_sorted)

    # Group variables by first dimension; move scalar variables first.
    dims_seen = {dim: i for i, dim in enumerate(dims_sorted)}

    def key(kv: tuple[Hashable, DataArray]) -> int:
        _, v = kv
        return dims_seen[v.dims[0]] if v.dims else -1

    for key_dim_idx, group in groupby(sorted(obj.data_vars.items(), key=key), key=key):
        group_vars = dict(group)

        # Unique dimensions for these variables that share the first dim,
        # ordered by first seen
        dims_unique = list(
            dict.fromkeys(dim for var in group_vars.values() for dim in var.dims)
        )
        dfs = []
        for k, v in group_vars.items():
            v = v.expand_dims("variable")
            v.coords["variable"] = [k]
            for dim in dims_unique:
                if dim not in v.dims:
                    v = v.expand_dims(dim)
                    v.coords[dim] = [""]
            if len(v.dims) > 2:
                v = v.stack(__col=["variable", *dims_unique[1:]])
            elif dims_unique:
                v = v.transpose(dims_unique[0], "variable")
            df = v.to_pandas()
            if not isinstance(df, pd.DataFrame):
                df = df.to_frame()
                df.columns.name = "variable"
                df.index = [""]
            dfs.append(df)

        df = pd.concat(dfs, axis=1)
        # Too many columns can block the web browser
        df = df.iloc[:, :100]

        if (
            (describe == "auto" and df.shape[0] > max_rows)
            # Never describe scalar variables
            or (describe is True and key_dim_idx != -1)
        ):
            for c in df.columns:
                if df[c].dtype == bool:
                    # Calculate mean etc.
                    df[c] = df[c].astype(int)
            df = df.describe()

        yield df


def display(
    obj: DataArray | Dataset,
    name: str | None = None,
    *,
    max_rows: int = 26,
    describe: bool | Literal["auto"] = "auto",
    transpose: bool = False,
) -> None:
    """Pretty-print a DataArray or Dataset in Jupyter Notebook.
    Unlike the default representation, this is more readable and shows the data.
    """
    from IPython.display import display_html  # noqa: PLC0415

    for df in _to_dataframes(obj, name=name, max_rows=max_rows, describe=describe):
        if transpose:
            html = df.T.to_html(max_cols=max_rows)
        else:
            html = df.to_html(max_rows=max_rows)
        display_html(html, raw=True)


@xarray.register_dataarray_accessor("display")
class DisplayAccessorDataArray:
    """Add .display(...) method to DataArray"""

    _obj: DataArray

    def __init__(self, obj: DataArray):
        self._obj = obj

    def __call__(
        self,
        name: str | None = None,
        *,
        max_rows: int = 26,
        describe: bool | Literal["auto"] = "auto",
        transpose: bool = False,
    ) -> None:
        display(
            self._obj,
            name=name,
            max_rows=max_rows,
            describe=describe,
            transpose=transpose,
        )


@xarray.register_dataset_accessor("display")
class DisplayAccessorDataset:
    """Add .display(...) method to Dataset"""

    _obj: Dataset

    def __init__(self, obj: Dataset):
        self._obj = obj

    def __call__(
        self,
        *,
        max_rows: int = 26,
        describe: bool | Literal["auto"] = "auto",
        transpose: bool = False,
    ) -> None:
        display(self._obj, max_rows=max_rows, describe=describe, transpose=transpose)
