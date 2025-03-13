<div align="center">
  <div>
    <h1 align="center">GGUF Converter</h1>
    <h4 align="center">Author <a href="https://waldomarais.com">Waldo Marais</a>
  </div>
	<h2>Convert Hugging Face models to GGUF format for use with LM Studio and other local inference engines</h2>
</div>

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

## Configuration

The script uses a `.env` file for configuration. Copy the example below and modify as needed:

```env
# Model Settings
MODEL_NAME=MACLAB-HFUT/PsycoLLM
OUTPUT_TYPE=q8_0

# Memory Settings
MAX_MEMORY_GB=16

# Directory Paths
MODELS_DIR=./downloaded_models
LLAMA_CPP_DIR=./llama.cpp
LM_STUDIO_DIR=~/.lmstudio/models

# Optional Settings
CLEANUP_AFTER_CONVERSION=false  # Set to true to remove downloaded files after conversion
```

### Configuration Options

- `MODEL_NAME`: The Hugging Face model to convert (e.g., "MACLAB-HFUT/PsycoLLM")
- `OUTPUT_TYPE`: The quantization format (see Output Types section below)
- `MAX_MEMORY_GB`: Maximum RAM to use during conversion
- `MODELS_DIR`: Where to store downloaded models
- `LLAMA_CPP_DIR`: Where to clone llama.cpp
- `LM_STUDIO_DIR`: Where to store converted models for LM Studio
- `CLEANUP_AFTER_CONVERSION`: Whether to delete downloaded files after conversion

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

1. Create and configure your `.env` file (see Configuration section)

2. Run the conversion script:
   ```bash
   python convert_to_gguf.py
   ```

3. The converted model will be saved in the LM Studio models folder specified in your .env file.

## Understanding Output Types (Quantization)

The `OUTPUT_TYPE` parameter determines the precision and size of your converted model. The currently available options in the latest llama.cpp are:

### Floating Point Formats

- **f32** (Full Precision)
  - 32-bit floating point representation
  - Highest accuracy but largest file size
  - Uses 4 bytes per weight
  - Best choice when accuracy is critical and storage space is not a concern
  - Rarely needed for inference

- **f16** (Half Precision)
  - 16-bit floating point representation
  - Good balance between accuracy and size
  - Uses 2 bytes per weight
  - Approximately 2x smaller than f32
  - Recommended for development and testing

- **bf16** (Brain Floating Point)
  - 16-bit brain floating point format
  - Similar size to f16 but with different numerical properties
  - Better handles large value ranges
  - Good for training and fine-tuning
  - Popular in modern AI hardware

### Quantized Formats

- **q8_0** (8-bit Quantization)
  - 8-bit fixed-point quantization
  - Uses 1 byte per weight
  - ~4x smaller than f32, ~2x smaller than f16
  - Good balance between quality and size
  - Recommended for most use cases
  - Minimal quality loss for most applications

- **tq1_0** (Tiny Quantization 1-bit)
  - 1-bit quantization (binary weights)
  - Extremely small file size (~32x smaller than f32)
  - Significant quality loss
  - Use only when storage space is extremely limited
  - Best for simple or small models

- **tq2_0** (Tiny Quantization 2-bit)
  - 2-bit quantization
  - Very small file size (~16x smaller than f32)
  - Better quality than tq1_0
  - Good for resource-constrained environments
  - Balance between extreme compression and usability

- **auto** (Automatic Selection)
  - Lets the converter choose the best format
  - Selection based on model architecture and size
  - Generally selects a good balance
  - Safe choice if unsure
  - May choose different formats for different parts of the model

### Size Comparison (Approximate)

For a 100MB base model size (f32):
- f32: 100MB (base size)
- f16/bf16: 50MB
- q8_0: 25MB
- tq2_0: 6.25MB
- tq1_0: 3.125MB

### How to Choose

1. **For Maximum Quality**
   - Use `f32` or `f16`
   - Best for research and development
   - When accuracy is critical

2. **For General Use**
   - Use `q8_0`
   - Good balance of size and quality
   - Recommended default choice

3. **For Minimum Size**
   - Use `tq1_0` or `tq2_0`
   - When storage space is very limited
   - Accept quality trade-offs

4. **When Unsure**
   - Use `auto`
   - Let the converter optimize
   - Safe default choice

### Tips

- Start with `q8_0` for most use cases
- If quality is insufficient, try `f16`
- If size is too large, try `tq2_0`
- Use `auto` if unsure about model requirements
- Test different formats to find the best balance for your specific use case