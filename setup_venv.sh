#!/bin/bash

# Shell script to create and set up a Python virtual environment
# Created: September 2, 2025

# Configuration
VENV_NAME="venv"
REQUIREMENTS_FILE="requirements.txt"

echo "Setting up Python virtual environment for robot-group-action-planner..."

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo "Found $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo "Found $PYTHON_VERSION"
else
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv $VENV_NAME
else
    echo "Virtual environment already exists: $VENV_NAME"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

# Check if requirements.txt exists and install dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "No $REQUIREMENTS_FILE found. Creating an empty one."
    cat > $REQUIREMENTS_FILE << EOF
# Python dependencies for robot-group-action-planner
# Add your dependencies below, for example:
# numpy==1.21.0
# pandas==1.3.0
EOF
fi

echo "Virtual environment setup complete!"
echo "To activate the virtual environment in the future, run: source $VENV_NAME/bin/activate"
