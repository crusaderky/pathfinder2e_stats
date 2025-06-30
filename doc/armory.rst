Armory
======
.. currentmodule:: pathfinder2e_stats

This is a collection of commonly-tested weapons, runes and spells.

For example, if you want a *+1 Striking Flaming Longsword*, you can use the following:

>>> from pathfinder2e_stats import armory
>>> flaming_longsword = armory.swords.longsword(2) + armory.runes.flaming()
>>> flaming_longsword
**Critical success:** (2d8)x2 slashing plus (1d6)x2 fire plus 1d10 persistent fire
**Success:** 2d8 slashing plus 1d6 fire

Note that this will always be incomplete. Feel free to open a PR to add more, but do expect to have to manually write your own damage profiles using :func:`Damage` for less common weapons and spells.

Axes
----
.. automodule:: pathfinder2e_stats.armory.axes
   :members:
   :undoc-members:

Bows
----
.. automodule:: pathfinder2e_stats.armory.bows
   :members:
   :undoc-members:

Crossbows
---------
.. automodule:: pathfinder2e_stats.armory.crossbows
   :members:
   :undoc-members:

Darts
-----
.. automodule:: pathfinder2e_stats.armory.darts
   :members:
   :undoc-members:

Hammers
-------
.. automodule:: pathfinder2e_stats.armory.hammers
   :members:
   :undoc-members:

Knives
------
.. automodule:: pathfinder2e_stats.armory.knives
   :members:
   :undoc-members:

Picks
-----
.. automodule:: pathfinder2e_stats.armory.picks
   :members:
   :undoc-members:

Swords
------
.. automodule:: pathfinder2e_stats.armory.swords
   :members:
   :undoc-members:

Property Runes
--------------
.. automodule:: pathfinder2e_stats.armory.runes
   :members:
   :undoc-members:

Cantrips
--------
.. automodule:: pathfinder2e_stats.armory.cantrips
   :members:
   :undoc-members:

Slot Spells
-----------
.. automodule:: pathfinder2e_stats.armory.spells
   :members:
   :undoc-members:

Class Features
--------------
These class features add damage of a specific type.
For class features that add flat damage to the weapon,
like a Barbarian's :prd_actions:`Rage <2802>`, see :doc:`tables`.

.. automodule:: pathfinder2e_stats.armory.class_features
   :members:
   :undoc-members:
