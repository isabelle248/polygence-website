#!/bin/bash

# Flow for input score + audio clip, output sharp/flat + timestamps

# Get arguments (user inputs: uploaded file path, tempo number)
PDF_FILE=$1

# PART 1 - parse sheet music using Audiveris

# Navigate to folder where pdf is (music)
cd ~/Documents/music

# Run Audiveris via Java
java -jar scripts/audiveris.jar -bath -export "$PDF_FILE"

# output final .mxl path to node
MXL_FILE="${PDF_FILE%.pdf}.mxl"
# Node can capture
echo "Generated MXL: $MXL_FILE"


# PART 2 - use pitch tracker to get frequencies from audio input
# (run python CREP script)
# python3 /Users/isabellelin/Documents/polygence_code/run_crepe.py > output1.txt
