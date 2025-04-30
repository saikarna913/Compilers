#!/bin/bash

# Check if a filename was provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh <filename> [--debug]"
    echo "Example: ./run.sh examples/hello.fs"
    exit 1
fi

FILENAME=$1
DEBUG_FLAG=""

# Check if debug flag is provided
if [ $# -gt 1 ] && [ "$2" == "--debug" ]; then
    DEBUG_FLAG="--debug"
fi

# Check if the file exists
if [ ! -f "$FILENAME" ]; then
    echo "Error: File '$FILENAME' not found."
    exit 1
fi

# Run the file using Python and main.py
python main.py "$FILENAME" $DEBUG_FLAG