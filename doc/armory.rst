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

Bow
^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.bow
   :members:

Brawling
^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.brawling
   :members:

Crossbow
^^^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.crossbow`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.crossbow
   :members:

Dart
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.dart`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.dart
   :members:

Hammer
^^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.hammer
   :members:

Knife
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.knife`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.knife
   :members:

Pick
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.pick`.

.. automodule:: pathfinder2e_stats.armory.pathfinder.pick
   :members:

Shield
^^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.shield
   :members:

Sword
^^^^^
.. automodule:: pathfinder2e_stats.armory.pathfinder.sword
   :members:


Starfinder weapons
------------------
Starfinder weapons are available under ``armory.starfinder.<group>.<weapon>``.

Axe
^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.axe
   :members:

Brawling
^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.brawling
   :members:

Club
^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.club
   :members:

Corrosive
^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.corrosive
   :members:

Crossbow
^^^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.crossbow`.

.. automodule:: pathfinder2e_stats.armory.starfinder.crossbow
   :members:

Cryo
^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.cryo
   :members:

Dart
^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.dart`.

.. automodule:: pathfinder2e_stats.armory.starfinder.dart
   :members:

Flail
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.flail
   :members:

Flame
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.flame`.

.. automodule:: pathfinder2e_stats.armory.starfinder.flame
   :members:

Hammer
^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.hammer
   :members:

Knife
^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.knife`.

.. automodule:: pathfinder2e_stats.armory.starfinder.knife
   :members:

Laser
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.laser
   :members:

Plasma
^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.plasma`.

.. automodule:: pathfinder2e_stats.armory.starfinder.plasma
   :members:

Polearm
^^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.polearm
   :members:

Projectile
^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.projectile
   :members:

Shield
^^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.shield
   :members:

Shock
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.shock
   :members:

Sniper
^^^^^^
See also: :func:`pathfinder2e_stats.armory.critical_specialization.sniper`.

.. automodule:: pathfinder2e_stats.armory.starfinder.sniper
   :members:

Sonic
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.sonic
   :members:

Spear
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.spear
   :members:

Sword
^^^^^
.. automodule:: pathfinder2e_stats.armory.starfinder.sword
   :members:


Class features
--------------
These class features add damage of a specific type.
For class features that add flat damage to the weapon,
like a Barbarian's :prd_actions:`Rage <2802>`, see :doc:`notebooks/tables`.

.. automodule:: pathfinder2e_stats.armory.class_features
   :members:

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

Weapon property runes
^^^^^^^^^^^^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.runes
   :members:

Cantrips
^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.cantrips
   :members:

Slot spells
^^^^^^^^^^^
.. automodule:: pathfinder2e_stats.armory.spells
   :members:
