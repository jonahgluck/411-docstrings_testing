#!/bin/bash

# Set the name of the virtual environment directory
VENV_DIR="meal_max_venv"
REQUIREMENTS_FILE="requirements.lock"
TEST_DIR="tests"  # Directory containing the test files

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python -m venv "$VENV_DIR"

  source "$VENV_DIR/bin/activate"

  # Install dependencies from requirements.lock if it exists
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --no-cache-dir -r "$REQUIREMENTS_FILE"
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi
else
  source "$VENV_DIR/bin/activate"
  echo "Virtual environment already exists. Activated."
fi

# Run the unit tests
if [ -d "$TEST_DIR" ]; then
  echo "Running unit tests..."
  python -m unittest discover -s "$TEST_DIR"
else
  echo "Error: Test directory '$TEST_DIR' not found."
  exit 1
fi
