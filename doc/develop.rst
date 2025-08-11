Development Guidelines
======================

Reporting issues
----------------

``pathfinder2e_stats`` strives to be faithful to the Pathfinder 2e rules as written
(RAW), as of the latest edition of the manuals plus the official errata and
clarifications. Deviation from the RAW should be treated as a bug.

If you find a bug or want to suggest a new feature, please report it on the
`GitHub issues page <https://github.com/crusaderky/pathfinder2e_stats/issues>`_.

Before you report an issue, please check if it can still be reproduced with the
latest version of this software.

For bug reports, please include the following information:

- A description of the bug
- The expected behavior. In case of rules-related bugs, please include
  a link to the relevant rule(s) on `aonprd <https://2e.aonprd.com/>`_.
- The actual behavior
- Steps to reproduce the bug (preferably with a minimal example)
- Any relevant error messages or stack traces


Deploying a development environment
-----------------------------------

1. Clone this repository with git:

.. code-block:: bash

     git clone git@github.com:crusaderky/pathfinder2e_stats.git
     cd pathfinder2e_stats

2. `Install pixi <https://pixi.sh/latest/#installation>`_
3. To keep a fork in sync with the upstream source:

.. code-block:: bash

   cd pathfinder2e_stats
   git remote add upstream git@github.com:crusaderky/pathfinder2e_stats.git
   git remote -v
   git fetch -a upstream
   git checkout main
   git pull upstream main
   git push origin main


Test
----

Test using pixi:

.. code-block:: bash

   pixi run tests
   pixi run doctests

Test with coverage:

.. code-block:: bash

   pixi run coverage

Test with coverage and open HTML report in your browser:

.. code-block:: bash

   pixi run open-coverage


Code Formatting
---------------

This project uses several code linters (ruff, mypy, etc.), which are enforced by
CI. Developers should run them locally before they submit a PR, through the single
command

.. code-block:: bash

    pixi run lint

Optionally, you may wish to run the linters automatically every time you make a
git commit. This can be done by running:

.. code-block:: bash

   pixi run install-git-hooks

Now the code linters will be run each time you commit changes.
You can skip these checks with ``git commit --no-verify`` or with
the short version ``git commit -n``.


Documentation
-------------

Build the documentation in ``build/html`` using pixi:

.. code-block:: bash

    pixi run docs

Build the documentation and open it in your browser:

.. code-block:: bash

    pixi run open-docs
