.. currentmodule:: pathfinder2e_stats

What's New
==========

v0.2.0 (unreleased)
-------------------

**New features**

- Added progression for the :prd_feats:`Weapon Proficiency <5239>` feat to
  ``tables.PC.weapon_proficiency``
- Added table ``tables.SIMPLE_PC.class_DC``

- Added support for Starfinder:

  - Added ``boost dX`` trait to :class:`Damage`
  - Added ``primary_target`` parameter to :func:`check` and :func:`map_outcome`
    to more easily model the Soldier's Primary Target ability
  - Added Starfinder classes to ``tables.PC`` and ``tables.SIMPLE_PC``
  - Added table ``tables.EARN_INCOME.starfinder`` for Starfinder credits
  - Added two demo notebooks

**Breaking changes**

- ``tables.EARN_INCOME``: renamed variable ``income_earned`` to ``pathfinder``
- ``tables.PC.weapon_proficiency``, ``tables.SIMPLE_PC.weapon_attack_bonus``:
  variables ``fighter`` and ``gunslinger`` have gained a dimension
  ``category: [martial, advanced]``

**Bugfixes**

- ``tables.PC``: Fighters are Legendary in all martial weapons at level 19
- ``tables.SIMPLE_PC``: Thaumaturge now uses Charisma as their key ability


v0.1.1 (2025-08-11)
-------------------

Minor changes specific to pypi and conda.


v0.1.0 (2025-08-08)
-------------------

Initial release.
