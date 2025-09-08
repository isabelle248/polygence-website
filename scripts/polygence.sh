# !/bin/bash

# # Flow for input score, output mxl file

# # Get arguments (user inputs: uploaded file path, tempo number)
# PDF_FILE=$1

# OUTPUT_DIR="/app/uploads"

# # PART 1 - parse sheet music using Audiveris

# # Run Audiveris with full classpath to include lib dependencies
# audiveris -batch -export "$PDF_FILE" -output "$OUTPUT_DIR"


# # Output MXL path relative to uploads folder
# BASENAME=$(basename "$PDF_FILE" .pdf)
# MXL_FILE="$OUTPUT_DIR/$BASENAME.mxl"
# # Node can capture
# echo "Generated MXL: $MXL_FILE"






# Get arguments (user inputs: uploaded file path, tempo number)
PDF_FILE=$1

# PART 1 - parse sheet music using Audiveris

# Navigate to folder where pdf is (music)
cd ~/Documents/music

# Run Audiveris via Java
/Applications/Audiveris.app/Contents/MacOS/Audiveris -batch -export "$PDF_FILE"
# output final .mxl path to node
MXL_FILE="${PDF_FILE%.pdf}.mxl"
# Node can capture
echo "Generated MXL: $MXL_FILE"

