#! /bin/bash

venv=".venv"
wait_time=3m

if [ -d "$venv" ]; then
    echo "Activating virtual environment: $venv"
    source "$venv/bin/activate"
else
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    exit 1
fi

echo "Publishing English post..."
python3 -m src.core.publish en

echo "Waiting $wait_time for next publication..."
sleep $wait_time

echo "Publishing Spanish post..."
python3 -m src.core.publish es

deactivate
