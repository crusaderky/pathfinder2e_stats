# Script for self-contained deployment on Windows
# Install pixi in subfolder, deploy environment,
# and run pixi task from command line (default: Jupyter Lab)

# Move to directory of this script
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

$pixi = ".pixi\bin\pixi.exe"

# Download and install pixi locally
if (-not (Test-Path $pixi)) {
    $env:PIXI_HOME = ".pixi"
    $env:PIXI_NO_PATH_UPDATE = "1"
    New-Item -ItemType Directory -Force -Path ".pixi"
    powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
}

# Inject wheel if we are running in a self-contained deployment
if (-not (Test-Path "pathfinder2e_stats")) {
    $whl = Get-ChildItem -Filter *.whl | Select-Object -First 1
    if ($null -ne $whl) {
        & $pixi add --pypi "pathfinder2e_stats@file:$PWD\$($whl.Name)"
    }
}

# Run task from command line parameters (default: Jupyter Lab)
if ($args.Count -eq 0) {
    & $pixi run -e prod jupyter
} else {
    & $pixi run @args
}
