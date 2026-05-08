#!/bin/bash

# Robot Dance Show - Song Discovery Script
# Lists all available songs (performances) in the project.

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is 3 levels up from skills/robot-dance-show/scripts/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SONG_DIR="$PROJECT_ROOT/songs"

if [ ! -d "$SONG_DIR" ]; then
    echo "Error: Song directory not found at $SONG_DIR"
    exit 1
fi

echo "Available Robot Dance Shows:"
echo "----------------------------"
# List .mp4 files without extension for easier use with the launcher
ls "$SONG_DIR"/*.mp4 2>/dev/null | xargs -n 1 basename | sed 's/\.mp4$//'

if [ $? -ne 0 ]; then
    echo "(No songs found in $SONG_DIR)"
fi
