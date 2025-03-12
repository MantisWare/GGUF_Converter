# Hugging Face to GGUF Converter

This tool helps you convert Hugging Face models to GGUF format for use with LM Studio and other local inference engines.

## Prerequisites

- Python 3.8 or higher
- Git
- C++ compiler (for building llama.cpp)
- Sufficient disk space (models can be several GB)

## Quick Setup

### For macOS/Linux:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### For Windows:

```bash
# Run the setup script
setup.bat
```

## Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Clone and build llama.cpp:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make
   cd ..
   ```

## Usage

1. Edit the `convert_to_gguf.py` file to set your desired model and quantization:
   ```python
   MODEL_NAME = "MACLAB-HFUT/PsycoLLM"  # Change to your desired model
   OUTPUT_TYPE = "f16"  # Options: f16, q4_0, q4_K_M, q8_0, etc.
   ```

2. Run the conversion script:
   ```bash
   python convert_to_gguf.py
   ```

3. The converted model will be saved in the current directory and optionally moved to your LM Studio models folder.

## Troubleshooting

- If you encounter memory issues, try a smaller model or increase your system's swap space.
- For Windows users, you might need to use WSL (Windows Subsystem for Linux) to build llama.cpp.
- Make sure you have enough disk space for both the downloaded model and the converted GGUF file.

## License

This project uses llama.cpp which is licensed under MIT. Please respect the licenses of the models you convert.
