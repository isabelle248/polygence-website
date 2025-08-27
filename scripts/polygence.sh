#!/bin/bash

# Flow for input score + audio clip, output sharp/flat + timestamps

# Install Audveris automatically on Render
AUDIVERIS_URL="https://github.com/Audiveris/audiveris/releases/download/5.6.2/Audiveris-5.6.2-ubuntu22.04-x86_64.deb"
AUDIVERIS_DEB="/tmp/audiveris.deb"

echo "Checking for Audiveris installation..."
if ! command -v audiveris &> /dev/null; then
    echo "Audiveris not found. Installing..."
    wget -q $AUDIVERIS_URL -O $AUDIVERIS_DEB
    sudo dpkg -i $AUDIVERIS_DEB || sudo apt-get install -f -y
    echo "Audiveris installed."
else
    echo "Audiveris already installed."
fi

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
