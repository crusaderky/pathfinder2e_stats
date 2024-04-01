import pytest
import xarray
from xarray.testing import assert_identical, assert_allclose

from pathfinder2e_stats import value_counts  # noqa: F401


@pytest.mark.parametrize("transpose", [False, True])
@pytest.mark.parametrize("use_accessor", [False, True])
@pytest.mark.parametrize("normalize", [False, True])
def test_value_count(transpose, use_accessor, normalize):
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

    if use_accessor:
        actual = a.value_counts("c", normalize=normalize)
    else:
        actual = value_counts(a, "c", normalize=normalize)

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
