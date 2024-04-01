API Reference
=============

Basic rolls
-----------
.. autofunction:: pathfinder2e_stats.roll

.. autofunction:: pathfinder2e_stats.d20


Checks
------
.. autofunction:: pathfinder2e_stats.sum_bonuses

.. autofunction:: pathfinder2e_stats.check

.. autoclass:: pathfinder2e_stats.DoS

.. autofunction:: pathfinder2e_stats.map_outcome


Damage rolls
------------
.. autoclass:: pathfinder2e_stats.Damage
    :members:
    :undoc-members:

.. autoclass:: pathfinder2e_stats.DamageList
    :members:
    :undoc-members:

.. autoclass:: pathfinder2e_stats.ExpandedDamage
    :members:
    :undoc-members:

.. autofunction:: pathfinder2e_stats.damage


Utilities
---------
.. autofunction:: pathfinder2e_stats.level2rank

.. autofunction:: pathfinder2e_stats.rank2level

.. autofunction:: pathfinder2e_stats.set_size


Xarray extensions
-----------------
When you ``import pathfinder2e_stats``, all DataArray and Dataset objects gain these
new methods:

.. function:: xarray.DataArray.value_counts(dim, *, new_dim="unique_value", normalize=False)

    Return the count of unique values for every point along dim, individually for
    each other dimension.

    This is conceptually the same as calling :meth:`pandas.Series.value_counts`
    individually for every series of a :class:`pandas.DataFrame` and then merging the
    output.

    :param dim:
        Name of the dimension to count the values along.
        It will be removed in the output array.
    :param new_dim:
        Name of the new dimension in the output array; defaults to ``unique_value``
    :param normalize:
        Return proportions rather than frequencies; defaults to False
    :returns:
        :class:`xarray.DataArray` with the same dimensions as the input array,
        minus dim, plus new_dim.
