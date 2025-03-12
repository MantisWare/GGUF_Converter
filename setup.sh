#!/bin/bash

# Create and activate virtual environment (optional)
echo "Setting up virtual environment (optional)..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Clone llama.cpp if not already present
if [ ! -d "llama.cpp" ]; then
    echo "Cloning llama.cpp repository..."
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    make
    cd ..
fi

echo "✅ Setup complete! You can now run the script with: python convert_to_gguf.py" 