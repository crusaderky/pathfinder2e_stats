import pytest
import xarray
from xarray.testing import assert_allclose, assert_identical

import pathfinder2e_stats  # noqa: F401


@pytest.mark.parametrize("transpose", [False, True])
@pytest.mark.parametrize("normalize", [False, True])
def test_value_counts(transpose, normalize):
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

    actual = a.value_counts("c", normalize=normalize)
    expect = xarray.DataArray(
        [
            [0, 1, 2, 3],
            [2, 4, 0, 0],
        ],
        dims=["r", "unique_value"],
        coords={"r": ["r0", "r1"], "unique_value": [0, 1, 2, 5]},
        attrs={"foo": "bar"},
    )

    if normalize:
        assert_allclose(expect / 6.0, actual)
    else:
        assert_identical(expect, actual)
