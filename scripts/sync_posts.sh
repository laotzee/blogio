#!/bin/bash

ENV_FILE=".env"

if [ -z "$1" ]; then
    echo "Error: Please provide a language argument ('en' or 'es')."
    exit 1
fi

if [ $1 = 'en' ]; then
    lang='en'
elif [ $1 = 'es' ]; then
    lang='es'
else
    echo 'No proper argument given'
    exit 1
fi

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "Warning: .env file not found at $ENV_FILE."
fi

target_dir="./resources/writing/$lang"
repo_dir="$HOME/$POST_SOURCE"
post_dir="$repo_dir/$lang"
time_frame="-20"
current_dir=$(pwd)

cd $repo_dir
git pull
cd $current_dir

mkdir -p "$target_dir"

find "$post_dir" -mmin "$time_frame" -type f -iname "*.md" -exec cp -t "$target_dir" {} +

if [ $? -eq 0 ]; then
    echo "✅ Successfully moved all found $lang files to $target_dir"
else
    echo "❌ An error occurred during the move operation."
fi
