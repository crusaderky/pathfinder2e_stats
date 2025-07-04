Installation
============

If you're new to Python
-----------------------
1. Install `Anaconda <https://www.anaconda.com/download>`_
2. Open the Anaconda terminal prompt
3. Execute

   .. code-block:: bash

        $ conda install -c conda-forge pathfinder2e_stats jupyterlab matplotlib hvplot scipy
        $ jupyter lab

4. Create a new notebook; then in the first cell run

    .. code-block:: python

        import pathfinder2e_stats as pf2

   and start hacking! Now read :doc:`notebooks/getting_started`.

Required dependencies
---------------------
- Python 3.11 or later
- `xarray <https://xarray.pydata.org/>`_

Recommended dependencies
------------------------
- `jupyterlab <https://jupyter.org/>`_ or `spyder <https://www.spyder-ide.org/>`_
- matplotlib, plotly, hvplot, or some other plotting library for visualizations

Installing with conda
---------------------
.. code-block:: bash

    conda install pathfinder2e_stats

Installing with pip
-------------------
.. code-block:: bash

    pip install pathfinder2e_stats

.. _mindeps_policy:

Minimum dependency versions
---------------------------
This project adopts a rolling policy based on `SPEC 0
<https://scientific-python.org/specs/spec-0000/>`_ regarding the minimum
supported version of its dependencies.

You can see the actual minimum tested versions in `pyproject.toml
<https://github.com/crusaderky/pathfinder2e_stats/blob/main/pyproject.toml>`_.
