#! /bin/bash

venv=".venv"
if [ -d "$venv" ]; then
    source "$venv/bin/activate"
else
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    echo "No scripts work without the activation of VENV"
    exit 1
fi

logo=" _     _             _       
| |   | |           (_)      
| |__ | | ___   ____ _  ___  
|  _ \| |/ _ \ / _  | |/ _ \ 
| |_) ) | |_| ( (_| | | |_| |
|____/ \_)___/ \___ |_|\___/ 
              (_____|        "

show_menu() {
    echo "Please enter an option"
    echo "[1] Initiate database"
    echo "[2] Execute pipeline"
    echo "[3] Sync new posts"
    echo "[4] Process quotes"
    echo "[0] Close menu"
}


declare active=1
declare option

while [ $active -eq 1 ]; do
    echo "$logo"
    show_menu
    read option
    clear
    if [[ $option =~ ^[0-4]$ ]]; then
        if [ $option -eq 0 ]; then
            active=0 
        elif [ $option -eq 1 ]; then
            bash scripts/initiate_db.sh
        elif [ $option -eq 2 ]; then
            bash scripts/run.sh
        elif [ $option -eq 3 ]; then
            bash scripts/sync_posts.sh en
            bash scripts/sync_posts.sh es
        elif [ $option -eq 4 ]; then
            bash scripts/process_quotes.sh
        fi
    else
        echo "No proper option selected"
    fi
done

deactivate
