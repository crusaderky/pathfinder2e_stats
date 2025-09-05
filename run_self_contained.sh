#!/bin/sh
# Script for self-contained deployment
# Install pixi in subdirectory, deploy environment,
# and run pixi task from command line (default: Jupyter Lab)

set -o errexit

# Move to directory of this script
cd "$(dirname "$0")"

PIXI=.pixi/bin/pixi

# Download and install pixi locally
if [ ! -f $PIXI ]; then
    mkdir -p .pixi
    curl -fsSL https://pixi.sh/install.sh | PIXI_HOME=.pixi PIXI_NO_PATH_UPDATE=1 sh
fi

# Inject wheel if we are running in a self-contained deployment
# (see `self-contained` pixi task)
if [ ! -d pathfinder2e_stats ]; then
    $PIXI add --pypi pathfinder2e_stats@file:$PWD/$(ls *.whl)
fi

# Run task from command line parameters (default: Jupyter Lab)
$PIXI run ${@:- -e prod jupyter}
