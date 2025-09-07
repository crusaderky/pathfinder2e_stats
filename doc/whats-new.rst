.. currentmodule:: pathfinder2e_stats

What's New
==========

v0.2.0 (unreleased)
-------------------

**New features**

- Added support for **Starfinder**:

  - Core mechanics:

    - Added ``boost dX`` trait to :class:`Damage`
    - Added ``primary_target`` parameter to :func:`check` and :func:`map_outcome`
      to more easily model the Soldier's Primary Target ability

  - :doc:`armory`:

    - Starfinder weapons added to ``armory.starfinder``
    - Starfinder Operative features and feats added to
      ``armory.class_features.operative``

  - :doc:`notebooks/tables`: Starfinder content is featured side by side with
    Pathfinder content.

    - Added Starfinder classes to ``tables.PC`` and ``tables.SIMPLE_PC``;
    - Added table ``tables.SIMPLE_PC.area_fire_DC``
    - Added table ``tables.EARN_INCOME.starfinder`` for Starfinder credits

  - Added a few demo notebooks for the Soldier

- Pathfinder and shared features:

  - Added progression for the :prd_feats:`Weapon Proficiency <5239>` feat to
    ``tables.PC.weapon_proficiency``
  - Added table ``tables.SIMPLE_PC.class_DC``
  - Added more Pathfinder weapons to the :doc:`armory`

**Breaking changes**

- The :doc:`armory` has been reorganized:

  - Since weapons are completely distinct between Pathfinder and Starfinder, and even
    when mixing classes etc. one would typically pick one content or the other,
    ``armory.knives.dagger`` has been moved to ``armory.pathfinder.knife.dagger``, etc.;
    Note the change from plural to singular for the weapon group.
  - Weapon critical specialization on the other hand is the same between the two games
    (with just extra entries for Starfinder), so
    ``armory.knives.critical_specialization`` has been moved to
    ``armory.critical_specialization.knife``, etc.
  - Class features have been broken down by class.
    ``armory.class_features.sneak_attack`` has been moved to
    ``armory.class_features.rogue.sneak_attack``, etc.

- :doc:`notebooks/tables` tweaks:

  - ``tables.EARN_INCOME.income_earned`` has been renamed to
    ``tables.EARN_INCOME.pathfinder`` to make room for its ``starfinder`` counterpart.
  - ``tables.PC.weapon_proficiency``, ``tables.SIMPLE_PC.weapon_attack_bonus``:
    variables ``fighter`` and ``gunslinger`` have gained dimension
    ``category: [martial, advanced]``

**Bugfixes**

- ``tables.PC``: Fighters are Legendary in all martial weapons at level 19
- ``tables.SIMPLE_PC``: Thaumaturge now uses Charisma as their key ability
- Removed spurious objects from IPython type hints in ``armory``


v0.1.1 (2025-08-11)
-------------------

Minor changes specific to pypi and conda.


v0.1.0 (2025-08-08)
-------------------

Initial release.
