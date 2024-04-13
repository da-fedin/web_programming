#!/bin/bash

echo "Build started"

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies using pip
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate

echo "Jupyter and requirements installed"
echo "Build completed"