pathfinder2e_stats: Statistical tools for Pathfinder
====================================================

``pathfinder2e_stats`` is a data science library for the
`Pathfinder <https://paizo.com/pathfinder/>`_ tabletop role-playing game (TTRPG),
second edition.
It is a toolkit to apply numerical statistical analysis to the game,
using industry standard technology stack and best practices.

It lets you answer questions such as:

- Is a certain action better than another, given some circumstances?
  E.g. what's the mean damage of a :prd_feats:`Vicious Swing <4775>` with a greatsword,
  compared to :prd_feats:`Double Slice <4769>` with a longsword and a shortsword?
- What's the chance of fully completing a complicated activity that implies many
  steps each with a chance of failure, e.g. :prd_feats:`Godbreaker <6049>`?
- What are the odds that a certain monster will instantly kill a player character
  in a single round?
- How much extra damage does a +1 to hit translate to?
  (and why is it 15% in most cases?)

While it *can* be used by powerplayers to optimize their characters, it is mainly
intended for people with a passion for numbers who want to reverse-engineer the game
balance, as well as for game masters who want to better tweak the challenge level of
their homebrew content.

What this software is not
-------------------------
- This is not a virtual tabletop (VTT);
- This is not a character builder;
- This is not an encounter builder;
- This is not a rules reference.


Intended audience
-----------------
``pathfinder2e_stats`` is intended for Pathfinder players and game masters
who are also familiar with data science workflows.
At the bare minimum, you need to be comfortable with one of the following
technology stacks:

- Python + pandas + Jupyter (or Spyder) workflows
- R + RStudio
- Matlab

**If you have no idea what any of the above means, this software is not for you.**

``pathfinder2e_stats`` is built on top of `xarray <https://xarray.pydata.org/>`_.
If you're not familiar with xarray, but you're already proficient with `pandas
<https://pandas.pydata.org/>`_, you should be able to pick it up quickly by reading the
`xarray tutorials <https://docs.xarray.dev/en/stable/getting-started-guide/index.html>`_.
If you're not familiar with Python, but you're proficient with R or Matlab, you can
catch up with one of the many Python for data science books or courses available online.

**This documentation does not cover generic xarray data science workflows.**
For example, here you will find out how to simulate 100,000 times the damage done by a
certain weapon to a monster, but aggregating the results and extracting insights
(calculating the mean, standard deviation, quintiles, plotting the distribution, etc.)
is up to you - on the basis that there is nothing special about it; it's just a regular
data science problem.


Table of contents
-----------------

.. toctree::
   :maxdepth: 1

   installing
   getting-started
   api
   armory
   tables
   notebooks/index
   develop
   whats-new


License
-------

pathfinder2e_stats is available under the open source `Apache License`__.

__ http://www.apache.org/licenses/LICENSE-2.0.html
