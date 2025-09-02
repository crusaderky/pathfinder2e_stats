.. currentmodule:: pathfinder2e_stats

What's New
==========

v0.2.0 (unreleased)
-------------------

- Added progression for the :prd_feats:`Weapon Proficiency <5239>` feat to
  ``tables.PC.weapon_proficiency``.
- Added support for Starfinder:

  - Added ``boost dX`` trait to :class:`Damage`
  - Added ``primary_target`` parameter to :func:`check` and :func:`map_outcome`
    to more easily model the Soldier's Primary Target ability.
  - Added two demo notebooks.
  - New table ``pf2.tables.EARN_INCOME.starfinder`` for Starfinder credits.

**Breaking changes:**

- Renamed ``pf2.tables.EARN_INCOME.income_earned`` to
  ``pf2.tables.EARN_INCOME.pathfinder``.


v0.1.1 (2025-08-11)
-------------------

Minor changes specific to pypi and conda.


v0.1.0 (2025-08-08)
-------------------

Initial release.
