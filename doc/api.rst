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

.. autofunction:: pathfinder2e_stats.value_counts
