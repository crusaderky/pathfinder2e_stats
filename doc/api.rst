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

.. class:: xarray.DataArray
    .. method:: value_counts(dim, *, new_dim="unique_value")

        Return the count of unique values for every point along dim, individually for
        each other dimension. This is conceptually the same as calling
        :meth:`pandas.Series.value_counts` individually for every series of a
        :class:`pandas.DataFrame` and then merging the output.
