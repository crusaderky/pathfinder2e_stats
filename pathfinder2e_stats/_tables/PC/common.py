from collections.abc import Collection

import xarray

MARTIAL = "$martial"
SPELLCASTER = "$spellcaster"

CLASSES = [
    # (class name, template it expands to)
    ("alchemist", MARTIAL),
    ("animist", SPELLCASTER),
    ("barbarian", MARTIAL),
    ("bard", SPELLCASTER),
    ("champion", MARTIAL),
    ("cleric", None),
    ("commander", MARTIAL),
    ("druid", SPELLCASTER),
    ("exemplar", MARTIAL),
    ("fighter", MARTIAL),
    ("guardian", MARTIAL),
    ("gunslinger", MARTIAL),
    ("inventor", MARTIAL),
    ("investigator", MARTIAL),
    ("kineticist", None),
    ("magus", None),
    ("monk", MARTIAL),
    ("oracle", SPELLCASTER),
    ("psychic", SPELLCASTER),
    ("ranger", MARTIAL),
    ("rogue", MARTIAL),
    ("sorcerer", SPELLCASTER),
    ("summoner", None),
    ("swashbuckler", MARTIAL),
    ("thaumaturge", MARTIAL),
    ("witch", SPELLCASTER),
    ("wizard", SPELLCASTER),
]


def postproc_classes(
    ds: xarray.Dataset,
    *,
    extra_columns: Collection[str] = (),
    only_spellcasters: bool = False,
) -> None:
    """Post-process a table that contains exactly one column per class:

    - Merge class/subclass columns into single variables with an extra dimension
    - Expand $martial and $spellcaster templates to omitted classes
    - Sort alphabetically
    - Test for missing classes
    """
    to_delete = set()

    # Merge class/subclass columns into single variables with an extra dimension
    for class_name, dim, subclasses in (
        ("cleric", "doctrine", ["battle creed", "cloistered cleric", "warpriest"]),
        ("fighter", "mastery", ["mastery", "other"]),
        ("gunslinger", "mastery", ["mastery", "other"]),
    ):
        if f"{class_name}/{subclasses[0]}" in ds:
            ds[class_name] = xarray.concat(
                [ds[f"{class_name}/{subclass}"] for subclass in subclasses],
                dim=dim,
            ).T
            to_delete |= {f"{class_name}/{subclass}" for subclass in subclasses}
            ds[dim] = subclasses

    if "mastery" in ds:
        ds["mastery"] = [True, False]

    # Expand $martial and $spellcaster templates to omitted classes
    for class_name, tpl in CLASSES:
        if class_name not in ds and tpl is not None and tpl in ds:
            ds[class_name] = ds[tpl]
            to_delete.add(tpl)

    for col_name in to_delete:
        del ds[col_name]

    # Sort alphabetically and test for missing classes
    vars = {}
    for class_name, tpl in CLASSES:
        if class_name in ds:
            vars[class_name] = ds[class_name]
            del ds[class_name]
        elif not only_spellcasters or tpl == SPELLCASTER:
            raise KeyError(class_name)  # pragma: no cover

    # Move extra columns to the end
    for col_name in extra_columns:
        vars[col_name] = ds[col_name]
        del ds[col_name]

    # Test for unexpected columns
    assert not ds.data_vars, f"Unexpected columns: {list(ds.data_vars)}"

    ds.update(vars)
