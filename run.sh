#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the conversion script
python convert_to_gguf.py

# Keep terminal open if running by double-click
read -p "Press Enter to exit..." 