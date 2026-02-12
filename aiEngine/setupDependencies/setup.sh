#!/bin/bash

SCRIPT_PATH=$(readlink -f "$0")
AI_ENGINE_DIR=$(dirname "$(dirname "$SCRIPT_PATH")")
PROJECT_ROOT=$(dirname "$AI_ENGINE_DIR")

cd "$PROJECT_ROOT" || exit

# Create virtual environment if necessary
if [ ! -d "aiEngine/unibot-venv" ]; then
    python3 -m venv aiEngine/unibot-venv
    echo "Virtual Environment created: $PROJECT_ROOT/aiEngine/unibot-venv."
else
    echo "Virtual Environment already created."
fi

# Activate unibot-venv
source "$PROJECT_ROOT/aiEngine/unibot-venv/bin/activate"
echo "Virtual Environment ready."

# Update pip & Install Dependencies
pip install --upgrade pip
pip install -r aiEngine/setupDependencies/requirements.txt
echo "Packages and Dependencies installed."