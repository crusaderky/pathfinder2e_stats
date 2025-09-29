Installation
============

If you're new to Python
-----------------------
You don't need to install anything to start using pathfinder2e-stats.
Just follow these steps:

1. Open the `web-based JupyterLite page
   <https://crusaderky.github.io/pathfinder2e_stats>`_
2. Create a new notebook or open a demo one
3. In the first cell, execute

    .. code-block:: python

        %pip install -q pathfinder2e-stats
        import pathfinder2e_stats as pf2

   and start hacking! Now read :doc:`getting_started`.


Local Installation
------------------
If you are more familiar with Python, it's recommended that you install the package
locally.

You can do this using either `conda <https://docs.conda.io>`_:

.. code-block:: bash

    conda install pathfinder2e-stats

or `pip <https://pip.pypa.io/>`_:

.. code-block:: bash

    pip install pathfinder2e-stats


Required dependencies
^^^^^^^^^^^^^^^^^^^^^
- Python 3.11 or later
- `xarray <https://xarray.pydata.org/>`_


Recommended dependencies
^^^^^^^^^^^^^^^^^^^^^^^^
- `jupyterlab <https://jupyter.org/>`_ or `spyder <https://www.spyder-ide.org/>`_
- matplotlib, plotly, hvplot, or some other plotting library for visualizations


.. _mindeps_policy:

Minimum dependency versions
^^^^^^^^^^^^^^^^^^^^^^^^^^^
This project adopts a rolling policy based on `SPEC 0
<https://scientific-python.org/specs/spec-0000/>`_ regarding the minimum
supported version of its dependencies.

You can see the actual minimum tested versions in `pyproject.toml
<https://github.com/crusaderky/pathfinder2e_stats/blob/main/pyproject.toml>`_.
