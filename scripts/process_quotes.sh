#!/bin/bash

venv=".venv"

src_path="src.core."
extraction_script="extractor"
background_script="background"
insertion_script="insertion"

echo "Extracting quotes from English posts..."
python -m "$src_path$extraction_script" en

echo "Extracting quotes from Spanish posts..."
python -m "$src_path$extraction_script" es

echo "Processing new backgrounds..."
python -m "$src_path$background_script"

echo "Preparing English posts..."
python -m "$src_path$insertion_script" en

echo "Preparing Spanish posts..."
python -m "$src_path$insertion_script" es
