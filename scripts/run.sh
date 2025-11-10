#! /bin/bash

venv=".venv"

bash ./scripts/sync_posts.sh es
bash ./scripts/sync_posts.sh en

if [ -d "$venv" ]; then
    echo "Activating virtual environment: $venv"
    source "$venv/bin/activate"
else
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    exit 1
fi

bash ./scripts/process_quotes.sh

deactivate


