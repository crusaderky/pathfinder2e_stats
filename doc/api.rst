API Reference
=============

Basic dice rolls
----------------
.. autofunction:: pathfinder2e_stats.roll
.. autofunction:: pathfinder2e_stats.d20


Degrees of Success
------------------
.. autoclass:: pathfinder2e_stats.DoS


Rolling checks
--------------
.. autofunction:: pathfinder2e_stats.check
.. autofunction:: pathfinder2e_stats.map_outcome
.. autofunction:: pathfinder2e_stats.outcome_counts
.. autofunction:: pathfinder2e_stats.sum_bonuses


Damage profiles
---------------
.. autoclass:: pathfinder2e_stats.Damage
    :members:
    :undoc-members:

.. autoclass:: pathfinder2e_stats.DamageList
    :members:
    :undoc-members:

.. autoclass:: pathfinder2e_stats.ExpandedDamage
    :members:
    :undoc-members:


Rolling for damage
------------------
.. autofunction:: pathfinder2e_stats.damage


Utility functions
-----------------
.. autofunction:: pathfinder2e_stats.level2rank
.. autofunction:: pathfinder2e_stats.rank2level


Xarray extensions
-----------------
When you ``import pathfinder2e_stats``, all DataArray and Dataset objects gain these
new methods:

.. _value_counts:

.. function:: xarray.DataArray.value_counts(dim: Hashable, *, new_dim: Hashable = "unique_value", normalize: bool = False) -> xarray.DataArray

    Return the count of unique values for every point along dim, individually for
    each other dimension.

    This is conceptually the same as calling :meth:`pandas.Series.value_counts`
    individually for every series of a :class:`~pandas.DataFrame` and then merging the
    output.

    :param dim:
        Name of the dimension to count the values along.
        It will be removed in the output array.
    :param new_dim:
        Name of the new dimension in the output array. Default: ``unique_value``
    :param normalize:
        Return proportions rather than frequencies. Default: False
    :returns:
        :class:`~xarray.DataArray` with the same dimensions as the input array,
        minus dim, plus new_dim.


.. _display:

.. function:: xarray.DataArray.display(name: str = None, *, max_rows: int = 26, describe: bool | Literal["auto"] = "auto", transpose: bool = False) -> None

.. function:: xarray.Dataset.display(*, max_rows: int = 26, describe: bool | Literal["auto"] = "auto", transpose: bool = False) -> None

    Pretty-print the DataArray or Dataset in Jupyter notebook.
    Unlike the default xarray display, this method prioritizes observing the data
    rather than the structure.

    The longest dimension of the DataArray/Dataset is plotted on the rows; all other
    dimensions are stacked along the columns.
    Display multiple dataframes if there are variables that don't share the longest
    dimension.

    :param name:
        Override DataArray name. Not used for Datasets.
    :param max_rows:
        Maximum number of rows to display. Default: 26
    :param describe:

        ``auto`` (default)
            If the rows of a DataFrame are more than `max_rows`, replace them with a
            statistical summary (min, max, mean, etc.).
        True
            Always replace the rows regardless of number
        False
            Always show the individual rows, but potentially trim those in the middle
            if they're more than `max_rows`.

        See :meth:`pandas.DataFrame.describe` for details on the summary statistics.

    :param transpose:
        If True, transpose rows and columns just before displaying. Default: False


Configuration
-------------
.. autofunction:: pathfinder2e_stats.set_config
.. autofunction:: pathfinder2e_stats.get_config
.. autoclass:: pathfinder2e_stats.config.Config
    :members:
    :undoc-members:
.. autofunction:: pathfinder2e_stats.seed
