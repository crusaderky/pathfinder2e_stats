.. currentmodule:: pathfinder2e_stats

What's New
==========

v0.2.0 (2025-09-29)
-------------------

**New features**

- Added `web-based JupyterLite page <https://crusaderky.github.io/pathfinder2e_stats>`_
  that lets you run pathfinder2e-stats without installation

- Added support for **Starfinder**:

  - Core mechanics:

    - Added ``boost dX`` trait to :class:`Damage`
    - Added ``area_fire()`` method to :class:`Damage`, :class:`DamageList` and
      :class:`ExpandedDamage`
    - Added ``primary_target`` parameter to :func:`check` and :func:`map_outcome`
      to more easily model the Soldier's Primary Target ability

  - :doc:`armory`:

    - Starfinder weapons added to ``armory.starfinder``
    - Starfinder weapon critical specialization effects (*flame, plasma, sniper*)
      added to ``armory.critical_specialization``
    - Operative features and feats added to ``armory.class_features.operative``

  - :doc:`tables`: Starfinder content is featured side by side with
    Pathfinder content.

    - Added Starfinder classes to ``tables.PC`` and ``tables.SIMPLE_PC``;
    - Added table ``tables.SIMPLE_PC.area_fire_DC``
    - Added table ``tables.EARN_INCOME.starfinder`` for Starfinder credits

  - Added a few demo notebooks for the Soldier

- Pathfinder and shared features:

  - Added ``scatter`` trait to :class:`Damage`
  - Added progression for the :prd_feats:`Weapon Proficiency <5239>` feat to
    ``tables.PC.weapon_proficiency``
  - Added table ``tables.SIMPLE_PC.class_DC``

- The :doc:`armory` has been expanded and reorganized:

  - Since weapons are completely distinct between Pathfinder and Starfinder, and even
    when mixing classes etc. one would typically pick one content or the other,
    ``armory.knives.dagger`` has been moved to ``armory.pathfinder.melee.dagger``. Note
    how weapons are no longer broken by weapon group: while in Pathfinder one can guess
    most of the times to which group a weapon belongs to, this does not hold for
    Starfinder: the Battleglove is in the brawling group, but the Polyglove is shock;
    the Zero Knife is not a knife and the Skyfire Sword is not a sword; etc. So now
    there are only four weapon modules:

    - ``armory.pathfinder.melee``
    - ``armory.pathfinder.ranged``
    - ``armory.starfinder.melee``
    - ``armory.starfinder.ranged``

  - Weapon critical specialization on the other hand is the same between the two games
    (with just extra entries for Starfinder), so
    ``armory.knives.critical_specialization`` has been moved to
    ``armory.critical_specialization.knife``, and so on.
  - Class features have been broken down by class.
    ``armory.class_features.sneak_attack`` has been moved to
    ``armory.class_features.rogue.sneak_attack``, etc.
  - Added all current Pathfinder and Starfinder weapons
  - Added axe critical specialization effect

**Breaking changes**

- ``tables.EARN_INCOME.income_earned`` has been renamed to
  ``tables.EARN_INCOME.pathfinder`` to make room for its ``starfinder`` counterpart.
- ``tables.PC.weapon_proficiency``, ``tables.SIMPLE_PC.weapon_attack_bonus``:
  variables ``fighter`` and ``gunslinger`` have gained dimension
  ``category: [martial, advanced]``

**Bugfixes**

- Splash damage no longer damages secondary targets on a miss
- ``tables.PC``: Fighters are Legendary in all martial weapons at level 19
- ``tables.SIMPLE_PC``: Thaumaturge now uses Charisma as their key ability
- Removed spurious objects from IPython type hints in ``armory``


v0.1.1 (2025-08-11)
-------------------

Minor changes specific to pypi and conda.


v0.1.0 (2025-08-08)
-------------------

Initial release.
