from __future__ import annotations

from collections.abc import Hashable
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import xarray
from xarray import DataArray, Dataset

if TYPE_CHECKING:  # circular import
    from pathfinder2e_stats._tables import PCTables


@cache
def _get_df() -> pd.DataFrame:
    """Load the raw classes DataFrame from the CSV file."""
    fname = Path(__file__).parent / "simple_pc.csv"
    return pd.read_csv(fname, index_col=[0], header=[0, 1]).fillna("")


def _class_name(df: pd.DataFrame) -> DataArray:
    return DataArray(df.index.str.replace(r"/.*", "", regex=True)).rename(
        {"dim_0": "class"}
    )


def _get_ability_boosts(pctables: PCTables, df: pd.DataFrame) -> DataArray:
    return (
        pctables.ability_bonus.boosts.sel(initial=df["ability_bonus.boosts"].values)
        .rename({"initial": "class"})
        .drop_vars("class")
    )


def _get_ability_apex(pctables: PCTables, df: pd.DataFrame) -> DataArray:
    return pctables.ability_bonus.apex * DataArray(
        df["ability_bonus.apex"].values, dims=["class"]
    )


def _merge_components(components: dict[str, DataArray]) -> Dataset:
    ds = Dataset(components)
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

        level = da.level
        # gunslinger and operative are untrained in advanced weapons outside of
        # their mastery. Don't add level.
        level = xarray.where(
            (da.sel(component="proficiency", drop=True) == 0),
            0,
            level,
        )

        da = xarray.concat(
            [level.expand_dims({"component": ["level"]}), da],
            dim="component",
        )

        vars[class_name] = da

    ds = Dataset(dict(sorted(vars.items())))

    ds["component"] = ds["component"].astype("U")
    if "mastery" in ds.dims:
        return ds.transpose("level", "component", "mastery", ...)
    return ds.transpose("level", "component", ...)


def weapon_bonus(pctables: PCTables) -> Dataset:
    """Total attack bonus to weapon strikes for all classes, with strong assumptions"""
    df = _get_df()["strike"]

    components = {
        "proficiency": (
            pctables.weapon_proficiency.to_array("class").sel(
                {"class": _class_name(df)}
            )
        ),
        "ability_boosts": _get_ability_boosts(pctables, df),
        "ability_apex": _get_ability_apex(pctables, df),
        "item": (
            pctables.attack_item_bonus.to_array("variable")
            .sel(variable=df["attack_item_bonus"].values)
            .T.rename({"variable": "class"})
            .drop_vars("class")
        ),
    }

    return _merge_components(components)


def spell_bonus(pctables: PCTables, as_DC: bool) -> Dataset:
    """Total spell attack bonus / spell DC for all classes, with strong assumptions"""
    df = _get_df()["spell"]

    components = {}
    if as_DC:
        components["base_DC"] = DataArray(10)

    components.update(
        {
            "proficiency": xarray.concat(
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
            ).sortby("class"),
            "ability_boosts": _get_ability_boosts(pctables, df),
            "ability_apex": _get_ability_apex(pctables, df),
        }
    )

    res = _merge_components(components)

    # STR/DEX does not matter for spells
    res["gunslinger"] = res["gunslinger"].isel(ability=0, drop=True)
    del res["ability"]
    return res


def class_DC(pctables: PCTables) -> Dataset:
    """Total class DC for all classes, with strong assumptions"""
    df = _get_df()["class"]

    components = {
        "base_DC": DataArray(10),
        "proficiency": pctables.class_proficiency.to_array("class").sel(
            {"class": _class_name(df)}
        ),
        "ability_boosts": _get_ability_boosts(pctables, df),
        "ability_apex": _get_ability_apex(pctables, df),
    }

    return _merge_components(components)


def area_fire_DC(pctables: PCTables) -> Dataset:
    """Total Area Fire or Auto-Fire DC (Starfinder)"""
    ds = class_DC(pctables)
    tracking = pctables.attack_item_bonus.improvement.expand_dims(
        component=["tracking"]
    )
    tracking["component"] = tracking["component"].astype("U")
    tracking_ds = Dataset(dict.fromkeys(ds.data_vars, tracking))
    return xarray.concat([ds, tracking_ds], dim="component")


def impulse_bonus(pctables: PCTables, as_DC: bool) -> Dataset:
    """Total impulse attack bonus and impulse DC for kineticist and dedications"""
    cls_names = ["kineticist", "kineticist_dedication"]

    components = {"level": pctables.level}
    if as_DC:
        components["base_DC"] = DataArray(10)

    components.update(
        {
            "proficiency": (pctables.class_proficiency[cls_names].to_array("class")),
            "ability_boosts": pctables.ability_bonus.boosts.sel(initial=[4, 3])
            .rename({"initial": "class"})
            .drop_vars("class"),
            "ability_apex": xarray.concat(
                [
                    pctables.ability_bonus.apex,
                    xarray.zeros_like(pctables.ability_bonus.apex),
                ],
                dim="class",
            ),
        }
    )
    if not as_DC:
        components["gate_attenuator"] = pctables.attack_item_bonus.gate_attenuator

    da = xarray.concat(components.values(), dim="component", coords="all")
    da.coords["component"] = list(components)
    return da.to_dataset("class").transpose("level", "component")
