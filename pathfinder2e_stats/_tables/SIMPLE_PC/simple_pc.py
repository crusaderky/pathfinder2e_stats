from __future__ import annotations

from collections.abc import Hashable
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import xarray

if TYPE_CHECKING:  # circular import
    from pathfinder2e_stats._tables import PCTables


@cache
def _get_df() -> pd.DataFrame:
    """Load the raw classes DataFrame from the CSV file."""
    fname = Path(__file__).parent / "simple_pc.csv"
    return pd.read_csv(fname, index_col=[0], header=[0, 1]).fillna("")


def _class_name(df: pd.DataFrame) -> xarray.DataArray:
    return xarray.DataArray(df.index.str.replace(r"/.*", "", regex=True)).rename(
        {"dim_0": "class"}
    )


def _get_ability_boosts(pctables: PCTables, df: pd.DataFrame) -> xarray.DataArray:
    return (
        pctables.ability_bonus.boosts.sel(initial=df["ability_bonus.boosts"].values)
        .rename({"initial": "class"})
        .drop_vars("class")
    )


def _get_ability_apex(pctables: PCTables, df: pd.DataFrame) -> xarray.DataArray:
    return pctables.ability_bonus.apex * xarray.DataArray(
        df["ability_bonus.apex"].values, dims=["class"]
    )


def _get_proficiency(
    pctables: PCTables, df: pd.DataFrame, prof_name: str
) -> xarray.DataArray:
    prof = (
        getattr(pctables, prof_name).to_array("class").sel({"class": _class_name(df)})
    )
    mask = xarray.DataArray(df[prof_name].values, dims=["class"])
    return prof * mask


def _merge_components(components: dict[str, xarray.DataArray]) -> xarray.Dataset:
    ds = xarray.Dataset(components)
    df = _get_df()
    rows = []
    dim: Hashable

    ds_other = ds
    for class_name, dim in (
        ("alchemist", "research_field"),
        ("cleric", "_tmp_doctrine2"),
        ("gunslinger", "ability"),
    ):
        ds_i = ds.sel({"class": ds["class"] == class_name})
        ds_i = ds_i.rename({"class": dim})
        ds_i[dim] = [
            v.split("/")[1]
            for v in df.index.values.tolist()
            if v.startswith(class_name + "/")
        ]
        ds_i = ds_i.expand_dims({"class": [class_name]})
        ds_other = ds_other.sel({"class": ds_other["class"] != class_name})
        rows.append(ds_i)
    rows.append(ds_other)
    ds = xarray.concat(rows, dim="class").to_array("component").to_dataset("class")

    vars = {}
    for class_name, da in ds.data_vars.items():
        if class_name == "cleric":
            assert (da._tmp_doctrine2.values == da.doctrine.values).all()
            da = da.sel(_tmp_doctrine2=da.doctrine)
            del da.coords["_tmp_doctrine2"]

        for dim in list(da.dims):
            if dim not in ("level", "component") and (da.isel({dim: 0}) == da).all():
                da = da.isel({dim: 0}, drop=True)

        da = xarray.concat(
            [da.level.expand_dims({"component": ["level"]}), da],
            dim="component",
        )
        vars[class_name] = da

    ds = xarray.Dataset(dict(sorted(vars.items())))

    if "mastery" in ds.dims:
        return ds.transpose("level", "component", "mastery", ...)
    return ds.transpose("level", "component", ...)


def strike_attack_bonus(pctables: PCTables) -> xarray.Dataset:
    """Total strike attack bonus for all classes, with strong assumptions"""
    df = _get_df()["strike_bonus"]

    components = {}
    components["ability_boosts"] = _get_ability_boosts(pctables, df)
    components["ability_apex"] = _get_ability_apex(pctables, df)

    components["item"] = (
        pctables.attack_item_bonus.to_array("variable")
        .sel(variable=df["attack_item_bonus"].values)
        .T.rename({"variable": "class"})
        .drop_vars("class")
    )

    for prof_name in ("weapon_proficiency", "class_proficiency"):
        components[prof_name] = _get_proficiency(pctables, df, prof_name)

    return _merge_components(components)


def spell_attack_bonus(pctables: PCTables) -> xarray.Dataset:
    """Total spell attack bonus for all classes, with strong assumptions"""
    df = _get_df()["spell_bonus"]

    components = {}
    components["ability_boosts"] = _get_ability_boosts(pctables, df)
    components["ability_apex"] = _get_ability_apex(pctables, df)
    components["spell_proficiency"] = xarray.concat(
        [
            pctables.spell_proficiency.to_array("class").sel(
                {"class": _class_name(df[df.spell_proficiency == r"%class%"])}
            ),
            pctables.spell_proficiency.dedication
            * xarray.ones_like(
                _class_name(df[df.spell_proficiency == "dedication"]),
                dtype=int,
            ),
            pctables.spell_proficiency.dedication
            * xarray.zeros_like(
                _class_name(df[df.spell_proficiency == ""]),
                dtype=int,
            ),
        ],
        dim="class",
    ).sortby("class")
    components["class_proficiency"] = _get_proficiency(
        pctables, df, "class_proficiency"
    )

    return _merge_components(components)
