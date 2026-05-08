#!/bin/bash

# Robot Action Planner - Execution Script
# This script activates the virtual environment and runs the application.

VENV_DIR="venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup_venv.sh..."
    if [ -f "./setup_venv.sh" ]; then
        chmod +x ./setup_venv.sh
        ./setup_venv.sh
    else
        echo "Error: setup_venv.sh not found. Please ensure the project is correctly set up."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Run the application with all passed arguments
echo "Starting Robot Action Planner..."
python3 main.py "$@"

# Deactivate is not strictly necessary in a script that is about to exit,
# but it's good practice if this were being sourced.
# deactivate
