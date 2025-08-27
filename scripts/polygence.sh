#!/bin/bash

# Flow for input score + audio clip, output sharp/flat + timestamps

# Get arguments (user inputs: uploaded file path, tempo number)
PDF_FILE=$1

# PART 1 - parse sheet music using Audiveris

BASE_DIR="$(dirname "$0")"           # scripts/ folder
UPLOADS_DIR="$BASE_DIR/../uploads"   # relative to repo root

# Make sure uploads folder exists
mkdir -p "$UPLOADS_DIR"

# Run Audiveris with full classpath to include lib dependencies
java -cp "$BASE_DIR/audiveris.jar:$BASE_DIR/lib/*" Audiveris -batch -export "$PDF_FILE"

# Output MXL path relative to uploads folder
BASENAME=$(basename "$PDF_FILE" .pdf)
MXL_FILE="$UPLOADS_DIR/$BASENAME.mxl"
# Node can capture
echo "Generated MXL: $MXL_FILE"

# PART 2 - use pitch tracker to get frequencies from audio input
# (run python CREP script)
# python3 /Users/isabellelin/Documents/polygence_code/run_crepe.py > output1.txt
