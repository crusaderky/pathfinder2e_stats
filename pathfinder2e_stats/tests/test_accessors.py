import numpy as np
import pandas as pd
import pytest
import xarray
from pandas.testing import assert_frame_equal
from xarray.testing import assert_allclose, assert_identical

import pathfinder2e_stats  # Install accessors  # noqa: F401
from pathfinder2e_stats.accessors import _to_dataframes


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


def test_display_accessor(monkeypatch):
    html = []

    def mock_display_html(arg, *, raw=False):
        html.append(arg)
        assert raw

    monkeypatch.setattr("IPython.display.display_html", mock_display_html)

    xarray.DataArray([1, 2, 3], dims=["hello"]).display()
    assert "hello" in html[0]
    assert "(unnamed)" in html[0]
    html.clear()

    xarray.DataArray([1, 2, 3], dims=["hello"]).display("world")
    assert "(unnamed)" not in html[0]
    assert "world" in html[0]
    assert "mean" not in html[0]
    html.clear()

    xarray.DataArray(np.arange(100), dims=["hello"]).display()
    assert len(html[0].splitlines()) < 50
    assert "mean" in html[0]
    html.clear()

    xarray.DataArray(np.arange(100), dims=["hello"]).display(describe=False)
    assert len(html[0].splitlines()) < 130
    assert "mean" not in html[0]
    html.clear()

    xarray.DataArray(np.arange(100), dims=["hello"]).display(
        max_rows=40, describe=False
    )
    assert len(html[0].splitlines()) > 170
    assert len(html[0].splitlines()) < 200
    assert "mean" not in html[0]
    html.clear()

    xarray.DataArray(np.arange(100), dims=["hello"]).display(max_rows=100)
    assert len(html[0].splitlines()) > 400
    assert "mean" not in html[0]
    html.clear()

    xarray.DataArray(np.arange(100), dims=["hello"]).display(
        max_rows=999, describe=True
    )
    assert len(html[0].splitlines()) < 50
    assert "mean" in html[0]
    html.clear()

    xarray.Dataset({"hello": ("x", [1, 2, 3]), "world": ("x", [4, 5, 6])}).display()
    assert len(html) == 1
    assert "hello" in html[0]
    assert "world" in html[0]
    html.clear()

    xarray.Dataset({"hello": ("x", [1, 2, 3]), "world": ("y", [4, 5, 6])}).display()
    assert len(html) == 2
    assert "hello" in html[0]
    assert "world" not in html[0]
    assert "hello" not in html[1]
    assert "world" in html[1]
    html.clear()
    print("=" * 80)

    xarray.Dataset({"v": ("x", np.arange(100))}).display()
    assert len(html[0].splitlines()) < 50
    assert "mean" in html[0]
    html.clear()

    xarray.Dataset({"v": ("x", np.arange(100))}).display(max_rows=100)
    assert len(html[0].splitlines()) > 400
    assert "mean" not in html[0]
    html.clear()

    xarray.Dataset({"v": ("x", np.arange(100))}).display(describe=False)
    assert len(html[0].splitlines()) < 130
    assert "mean" not in html[0]
    html.clear()

    # Calculate mean etc. for boolean variables.
    # This is not the default behaviour in pandas.
    xarray.DataArray(np.arange(100) > 50).display()
    assert "mean" in html[0]
    html.clear()

    xarray.Dataset().display()
    assert not html

    with pytest.raises(TypeError, match="1 positional argument but 2 were given"):
        xarray.Dataset().display("foo")

    a = xarray.DataArray(np.arange(20))
    a.display()
    html_orig = html[0]
    html.clear()
    a.display(transpose=True)
    assert html[0] != html_orig
    html.clear()

    a = xarray.Dataset({"v": ("x", np.arange(20))})
    a.display()
    html_orig = html[0]
    html.clear()
    a.display(transpose=True)
    assert html[0] != html_orig
    html.clear()


def assert_frame_equal_anyint(df1, df2):
    """Variant of assert_frame_equal that ignores
    int32 vs int64 differences on old Windows stack.
    """
    for df in (df1, df2):
        for col in df.columns:
            if df[col].dtype == np.int32:
                df[col] = df[col].astype(np.int64)
        if not isinstance(df.index, pd.MultiIndex) and df.index.dtype == np.int32:
            df.index = df.index.astype(np.int64)
        if not isinstance(df.columns, pd.MultiIndex) and df.columns.dtype == np.int32:
            df.columns = df.columns.astype(np.int64)
    assert_frame_equal(df1, df2)


def test_to_dataframes():
    ds = xarray.Dataset(
        {
            "a": (("x", "y"), [[1, 2], [3, 4]]),
            "c": ("x", [9, 10]),
            "n": (("x", "z"), [[5, 6], [7, 8]]),
            "e": 13,
            "h": ("y", [11, 12]),
            "f": "foo",
        },
        coords={"x": [10, 20], "y": ["foo", "bar"]},
    )
    dfs = list(_to_dataframes(ds))
    assert len(dfs) == 3

    assert_frame_equal_anyint(
        dfs[0],
        pd.DataFrame(
            [[13, "foo"]],
            index=[""],
            columns=pd.Index(["e", "f"], name="variable"),
        ),
    )

    assert_frame_equal_anyint(
        dfs[1],
        pd.DataFrame(
            [
                [1, 2, 9, 5, 6],
                [3, 4, 10, 7, 8],
            ],
            index=pd.Index([10, 20], name="x"),
            columns=pd.MultiIndex.from_tuples(
                [
                    ("a", "foo", ""),
                    ("a", "bar", ""),
                    ("c", "", ""),
                    ("n", "", 0),
                    ("n", "", 1),
                ],
                names=("variable", "y", "z"),
            ),
        ),
    )

    assert_frame_equal_anyint(
        dfs[2],
        pd.DataFrame(
            [[11], [12]],
            index=pd.Index(["foo", "bar"], name="y"),
            columns=pd.Index(["h"], name="variable"),
        ),
    )


def test_to_dataframes_name():
    df = next(_to_dataframes(xarray.DataArray([1, 2])))
    assert_frame_equal_anyint(
        df,
        pd.DataFrame(
            [[1], [2]],
            index=pd.Index([0, 1], name="dim_0"),
            columns=pd.Index(["(unnamed)"], name="variable"),
        ),
    )

    df = next(_to_dataframes(xarray.DataArray([1, 2]), name="foo"))
    assert df.columns[0] == "foo"

    df = next(_to_dataframes(xarray.DataArray([1, 2], name="bar")))
    assert df.columns[0] == "bar"

    df = next(_to_dataframes(xarray.DataArray([1, 2], name="bar"), name="foo"))
    assert df.columns[0] == "foo"


def test_to_dataframes_max_rows():
    a = xarray.DataArray(np.arange(100))
    df = next(_to_dataframes(a))
    assert df.shape == (8, 1)
    assert "mean" in df.index

    df = next(_to_dataframes(a, describe=False))
    assert df.shape == (100, 1)

    df = next(_to_dataframes(a, max_rows=99))
    assert df.shape == (8, 1)
    assert "mean" in df.index

    df = next(_to_dataframes(a, max_rows=100))
    assert df.shape == (100, 1)

    df = next(_to_dataframes(xarray.DataArray([1, 2]), describe=True))
    assert df.shape == (8, 1)
    assert "mean" in df.index


@pytest.mark.parametrize("describe", [True, "auto", False])
def test_to_dataframes_scalar(describe):
    ds = xarray.Dataset(data_vars={"x": 1, "y": 2.5})
    df = next(_to_dataframes(ds, describe=describe))
    assert_frame_equal_anyint(
        df,
        pd.DataFrame(
            [[1, 2.5]],
            index=[""],
            columns=pd.Index(["x", "y"], name="variable"),
        ),
    )


def test_to_dataframes_describe_bool():
    """Unlike in pandas, describe() calculates the mean etc. of boolean variables."""
    a = xarray.DataArray(np.arange(100))
    a = a[a > 30]
    df = next(_to_dataframes(a))
    expect = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    assert df.index.values.tolist() == expect


def test_to_dataframes_reorder():
    ds = xarray.Dataset(
        {
            "a": (("z", "y"), np.arange(10).reshape(2, 5)),
            "b": (("y", "x"), np.arange(10, 20).reshape(5, 2)),
        },
    )
    dfs = list(_to_dataframes(ds))
    assert len(dfs) == 1
    assert_frame_equal_anyint(
        dfs[0],
        pd.DataFrame(
            [
                [0, 5, 10, 11],
                [1, 6, 12, 13],
                [2, 7, 14, 15],
                [3, 8, 16, 17],
                [4, 9, 18, 19],
            ],
            index=pd.Index([0, 1, 2, 3, 4], name="y"),
            columns=pd.MultiIndex.from_tuples(
                [
                    ("a", 0, ""),
                    ("a", 1, ""),
                    ("b", "", 0),
                    ("b", "", 1),
                ],
                # Preserve first seen order
                names=("variable", "z", "x"),
            ),
        ),
    )


def test_to_dataframes_max_cols():
    a = xarray.DataArray(np.arange(300 * 300).reshape(300, 300))
    df = next(_to_dataframes(a))
    assert df.shape == (8, 100)


def test_to_dataframes_dataarray_same_name():
    """Test special case of tables.PC.level"""
    a = xarray.DataArray([1, 2], dims=["level"], coords={"level": [1, 2]}, name="level")
    df = next(_to_dataframes(a))
    assert df.shape == (2, 1)
    assert df.index.name == "level"
    assert df.columns == pd.Index(["values"], name="variable")
