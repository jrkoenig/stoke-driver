#!/bin/bash

rm -f state.json
nohup python manager.py >manager.out & disown
sleep 0.5
nohup python worker.py localhost:8080 50 >worker.out & disown

#python manager.py &
#sleep 1
#python worker.py localhost:8080 50 &