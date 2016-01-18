#!/bin/sh

export PYTHONPATH="$PYTHONPATH:$HOME/py"
export PATH="$PATH:$HOME/expt/stoke/bin"
nohup python serversynth.py 1>server.log 2>&1 &
echo "Launched."
