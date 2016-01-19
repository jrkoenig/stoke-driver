#!/bin/sh

export PYTHONPATH="$PYTHONPATH:$HOME/py"
nohup python serversynth.py 1>server.log 2>&1 &
echo "Launched."
