@echo off

:: Activate virtual environment if it exists
if exist venv (
    call venv\Scripts\activate.bat
)

:: Run the conversion script
python convert_to_gguf.py

:: Keep console window open
pause 