Armory
======
This is a collection of commonly-tested weapons, runes, spells, and class features.

For example, if you want a *+1 Striking Flaming Longsword*, you can use the following:

>>> from pathfinder2e_stats import armory
>>> flaming_longsword = armory.pathfinder.sword.longsword(2) + armory.runes.flaming()
>>> flaming_longsword
**Critical success** (2d8)x2 slashing plus (1d6)x2 fire plus 1d10 persistent fire
**Success** 2d8 slashing plus 1d6 fire

This module will always be incomplete. Feel free to open a PR to add more, but do expect
to have to manually write your own damage profiles using
:class:`~pathfinder2e_stats.Damage` for less common weapons and spells.

Pathfinder weapons
------------------

Pathfinder weapons are available under ``armory.pathfinder.<group>.<weapon>``.

Axe
^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.axe
   :members:
   :undoc-members:

Bow
^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.bow
   :members:
   :undoc-members:

Crossbow
^^^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.crossbow`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.crossbow
   :members:
   :undoc-members:

Dart
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.dart`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.dart
   :members:
   :undoc-members:

Hammer
^^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.hammer
   :members:
   :undoc-members:

Knife
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.knife`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.knife
   :members:
   :undoc-members:

Pick
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.pick`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.pick
   :members:
   :undoc-members:

Sword
^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.sword
   :members:
   :undoc-members:


Starfinder weapons
------------------
Starfinder weapons are available under ``armory.starfinder.<group>.<weapon>``.

Club
^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.club
   :members:
   :undoc-members:

Crossbow
^^^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.crossbow`.

.. automodule:: pathfinder2e_stats.armory.starfinder.crossbow
   :members:
   :undoc-members:

Dart
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.dart`.

.. automodule:: pathfinder2e_stats.armory.starfinder.dart
   :members:
   :undoc-members:

Flame
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.flame`.

.. automodule:: pathfinder2e_stats.armory.starfinder.flame
   :members:
   :undoc-members:

Knife
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.knife`.

.. automodule:: pathfinder2e_stats.armory.starfinder.knife
   :members:
   :undoc-members:

Plasma
^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.plasma`.

.. automodule:: pathfinder2e_stats.armory.starfinder.plasma
   :members:
   :undoc-members:

Sniper
^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.sniper`.

.. automodule:: pathfinder2e_stats.armory.starfinder.sniper
   :members:
   :undoc-members:

Sword
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.sword
   :members:
   :undoc-members:


Other
-----

Weapon critical specialization effects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The critical specialization effect of these weapon groups simply add damage on a
critical hit. Other weapon groups add debuffs instead, which can't be simply modelled as
:class:`~pathfinder2e_stats.Damage` objects and must instead be handled as conditional
effects.

.. automodule:: pathfinder2e_stats.armory.critical_specialization
   :members:
   :undoc-members:

Weapon property runes
^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.runes
   :members:
   :undoc-members:

Cantrips
^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.cantrips
   :members:
   :undoc-members:

Slot spells
^^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.spells
   :members:
   :undoc-members:

Class features
^^^^^^^^^^^^^^
These class features add damage of a specific type.
For class features that add flat damage to the weapon,
like a Barbarian's :prd_actions:`Rage <2802>`, see :doc:`notebooks/tables`.

.. automodule:: pathfinder2e_stats.armory.class_features
   :members:
   :undoc-members:
