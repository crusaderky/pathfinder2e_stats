from collections.abc import Collection, Hashable, Mapping
from typing import TYPE_CHECKING, Literal, TypeVar

import xarray
from xarray import DataArray, Dataset

from pathfinder2e_stats.config import get_config

if TYPE_CHECKING:
    _T = TypeVar("_T", int, DataArray)
else:
    # Hack to fix Sphinx rendering
    _T = "int | DataArray"


def level2rank(level: _T, *, dedication: bool = False) -> _T:
    """Convert a creature's or item's level to their rank, e.g. to determine if they're
    affected by the incapacitation trait or to counteract their abilities. It can also
    be used to determine a spellcaster's maximum spell rank.

    :param level:
        The creature's level
    :param dedication:
        Set to True to return the highest spell slot rank of a character with
        spellcaster Dedication who took Basic, Expert and Master Spellcasting feats at
        levels 4, 12 and 18 respectively. Defaults to False.
    :returns:
        The creature's rank or spellcaster's maximum spell rank.
        Return type matches the type of `level`.
    """
    if dedication:
        res = xarray.where(
            level < 12,
            # FIXME np.clip() raises a DeprecationWarning vs. xarray
            DataArray(level // 2 - 1).clip(0, 3),
            level // 2 - 2,
        )
        return res if isinstance(level, DataArray) else res.item()

    return (level + 1) // 2


def rank2level(rank: _T, *, dedication: bool = False) -> _T:
    """Convert a spell or effect's rank to a creature's or item's maximum level in that
    rank, e.g. the maximum level of a creature that doesn't benefit from the
    incapacitation trait.

    Subtract one to the output for the minimum level in the same rank, or to determine
    the minimum level of a spellcaster in order to be able to cast a spell of a given
    rank.

    :param rank:
        The spell or effect's rank
    :param dedication:
        Set to True to return the level a character with spellcaster Dedication who took
        Basic, Expert and Master Spellcasting feats at levels 4, 12 and 18 respectively
        needs to be to gain a spell slot of this rank. Defaults to False.
    :returns:
        The creature's maximum level within the rank. Return type matches the type of
        `rank`.
    """
    if dedication:
        res = rank * 2 + xarray.where(rank < 4, 2, 4)
        return res if isinstance(rank, DataArray) else res.item()

    return rank * 2


def _parse_independent_dependent_dims(
    config_prefix: Literal["check", "damage"],
    ds: Dataset,
    independent_dims: Mapping[Hashable, int | None] | Collection[Hashable],
    dependent_dims: Collection[Hashable],
) -> dict[Hashable, int]:
    """Parse and validate the independent and dependent dimensions.

    This is an internal helper for :func:`check` and :func:`damage`.

    :param config_prefix:
        ``check`` or ``damage``
    :param ds:
        Dataset defininig the domain of the input dimensions
    :param independent_dims:
        See parameter description in :func:`check`
    :param dependent_dims:
        See parameter description in :func:`check`
    :returns:
        A dictionary of independent dimensions with their sizes.
    """
    cfg = get_config()
    ind_default = cfg[f"{config_prefix}_independent_dims"]  # type: ignore[literal-required]
    dep_default = cfg[f"{config_prefix}_dependent_dims"]  # type: ignore[literal-required]

    default_conflict = ind_default & dep_default
    if default_conflict:
        raise ValueError(
            f"Dimension(s) {sorted(default_conflict, key=str)} appear in config "
            f"in config key `{config_prefix}_independent_dims` as well as "
            f"`{config_prefix}_dependent_dims"
        )

    dim: Hashable
    for cont, label in (
        (independent_dims, "parameter `independent_dims`"),
        (dependent_dims, "parameter `dependent_dims`"),
        (ind_default, f"config key `{config_prefix}_independent_dims`"),
        (dep_default, f"config key `{config_prefix}_dependent_dims`"),
    ):
        if "roll" in cont:
            raise ValueError(
                "Dimension `roll` is always independent and must not be included "
                f"in {label}"
            )

    if isinstance(independent_dims, Mapping):
        out = dict(independent_dims)
        for dim, size in independent_dims.items():
            if size is None:
                out[dim] = ds.sizes[dim]
            elif dim in ds.sizes and ds.sizes[dim] != size:
                raise ValueError(
                    f"Dimension {dim!r} already exists with size "
                    f"{ds.sizes.get(dim, size)}, but {size=} was specified. "
                    "Set to None to automatically use the existing size."
                )
    else:
        out = {dim: ds.sizes[dim] for dim in independent_dims}

    dependent_dims = set(dependent_dims)

    for dim in ind_default:
        if dim in ds.sizes and dim not in dependent_dims:
            out.setdefault(dim, ds.sizes[dim])

    conflict = set(out) & dependent_dims
    missing = set(ds.sizes) - {"roll"} - set(out) - dependent_dims - dep_default
    unknown = dependent_dims - set(ds.sizes)
    if conflict:
        raise ValueError(
            f"Dimension(s) {sorted(conflict, key=str)} are both independent "
            "and dependent"
        )
    if missing:
        raise ValueError(
            f"Dimension(s) {sorted(missing, key=str)} must be listed in either "
            "independent_dims or dependent_dims. "
        )
    if unknown:
        raise KeyError(
            f"Dimension(s) {sorted(unknown, key=str)} are not present in the "
            "input dataset. "
        )

    return out
