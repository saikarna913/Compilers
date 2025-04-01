#!/bin/bash
# filepath: c:\Users\aatal\Desktop\Compilers\Project\Compilers\test.sh

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <filename.fs>"
    exit 1
fi

filename="$1"

if [[ "$filename" != *.fs ]]; then
    echo "Error: File must have a .fs extension."
    exit 1
fi

python flux.py "$filename"