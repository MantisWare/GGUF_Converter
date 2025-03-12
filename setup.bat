@echo off
echo Setting up environment for Hugging Face to GGUF conversion...

:: Create and activate virtual environment (optional)
echo Setting up virtual environment (optional)...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Clone llama.cpp if not already present
if not exist llama.cpp (
    echo Cloning llama.cpp repository...
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    :: Note: Windows users might need to install build tools or use WSL for make
    echo Note: You may need to build llama.cpp manually on Windows
    echo Please refer to llama.cpp documentation for Windows build instructions
    cd ..
)

echo ✅ Setup complete! You can now run the script with: python convert_to_gguf.py
pause 