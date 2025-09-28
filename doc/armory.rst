Armory
======
This is a collection of commonly-tested weapons, runes, spells, and class features.

For example, if you want a *+1 Striking Flaming Longsword*, you can use the following:

>>> from pathfinder2e_stats import armory
>>> flaming_longsword = armory.pathfinder.melee.longsword(2) + armory.runes.flaming()
>>> flaming_longsword
**Critical success** (2d8)x2 slashing plus (1d6)x2 fire plus 1d10 persistent fire
**Success** 2d8 slashing plus 1d6 fire

All functions in this module return pre-compiled :class:`~pathfinder2e_stats.Damage`
objects. This means that they're blind to any rune or trait that is not damage-related:
for example, there is nothing that distinguishes a +1 sword from a +2 sword, because the
attack bonus is not part of the damage profile, but impacts the `bonus` parameter of
:func:`~pathfinder2e_stats.check`. Likewise, there is no distinction here between agile
and non-agile weapons.

This module will always be incomplete. Feel free to open a PR to add more, but do expect
to have to manually write your own damage profiles using
:class:`~pathfinder2e_stats.Damage` for less common weapons and spells.

Pathfinder melee weapons
------------------------
.. automodule:: pathfinder2e_stats.armory.pathfinder.melee
   :members:

Pathfinder ranged weapons
-------------------------
.. automodule:: pathfinder2e_stats.armory.pathfinder.ranged
   :members:

Starfinder melee weapons
------------------------
.. automodule:: pathfinder2e_stats.armory.starfinder.melee
   :members:

Starfinder ranged weapons
-------------------------
.. automodule:: pathfinder2e_stats.armory.starfinder.ranged
   :members:

Weapon critical specialization effects
--------------------------------------
The critical specialization effect of these weapon groups simply add damage on a
critical hit. Other weapon groups add debuffs instead, which can't be simply modelled as
:class:`~pathfinder2e_stats.Damage` objects and must instead be handled as conditional
effects.

.. automodule:: pathfinder2e_stats.armory.critical_specialization
   :members:

Weapon property runes
---------------------
.. automodule:: pathfinder2e_stats.armory.runes
   :members:

Cantrips
--------
.. automodule:: pathfinder2e_stats.armory.cantrips
   :members:

Slot spells
-----------
.. automodule:: pathfinder2e_stats.armory.spells
   :members:

Class features
--------------
These class features add damage of a specific type.
For class features that add flat damage to the weapon,
like a Barbarian's :prd_actions:`Rage <2802>`, see :doc:`tables`.

Operative
^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.class_features.operative
   :members:

Rogue
^^^^^
.. automodule:: pathfinder2e_stats.armory.class_features.rogue
   :members:

Swashbuckler
^^^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.class_features.swashbuckler
   :members:
