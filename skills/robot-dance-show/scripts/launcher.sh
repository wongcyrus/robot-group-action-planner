#!/bin/bash

# Robot Dance Show - Skill Launcher
# This script ensures the performance runs within the project's virtual environment.

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is 3 levels up from skills/robot-dance-show/scripts/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
LOCK_FILE="/tmp/robot-dance-show.lock"

# Check if another instance is already running
if [ -f "$LOCK_FILE" ]; then
    # Check if the process recorded in the lock file is actually still running
    OLD_PID=$(cat "$LOCK_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Error: Another robot dance show is already running (PID: $OLD_PID)."
        echo "Please wait for it to finish or stop it before starting a new one."
        exit 1
    else
        # Stale lock file, remove it
        rm -f "$LOCK_FILE"
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please ensure the project is set up correctly before running this skill."
    exit 1
fi

# Create lock file with current PID
echo $$ > "$LOCK_FILE"

# Ensure lock file is removed on exit
trap "rm -f $LOCK_FILE" EXIT

# Set authorization for the internal runner
export ROBOT_DANCE_AUTHORIZED=true

# Run the internal runner using the venv's python executable
echo "Starting robot dance show using virtual environment: $VENV_PATH"
"$VENV_PATH/bin/python3" "$SCRIPT_DIR/_internal_runner.py" "$@"
