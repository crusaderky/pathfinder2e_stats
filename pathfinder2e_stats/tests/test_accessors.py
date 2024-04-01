import pytest
import xarray
from xarray.testing import assert_identical

import pathfinder2e_stats  # noqa: F401


@pytest.mark.parametrize("transpose", [False, True])
def test_value_count(transpose):
    a = xarray.DataArray(
        [
            [1, 2, 5, 5, 2, 5],
            [0, 1, 1, 0, 1, 1],
        ],
        dims=["r", "c"],
        coords={"r": ["r0", "r1"], "c": list(range(10, 70, 10))},
        attrs={"foo": "bar"},
    )
    if transpose:
        a = a.T

    assert_identical(
        a.value_counts("c"),
        xarray.DataArray(
            [
                [0, 1, 2, 3],
                [2, 4, 0, 0],
            ],
            dims=["r", "unique_value"],
            coords={"r": ["r0", "r1"], "unique_value": [0, 1, 2, 5]},
            attrs={"foo": "bar"},
        ),
    )
