import os
import subprocess
import sys
import gc
import shutil
from transformers import AutoModelForCausalLM, AutoTokenizer
import huggingface_hub
import torch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# STEP 1: Load configuration from .env
MODEL_NAME = os.getenv('MODEL_NAME', 'MACLAB-HFUT/PsycoLLM')  # Default value as fallback
OUTPUT_TYPE = os.getenv('OUTPUT_TYPE', 'q8_0')  # Default value as fallback
MAX_MEMORY_GB = int(os.getenv('MAX_MEMORY_GB', '16'))
CLEANUP_AFTER_CONVERSION = os.getenv('CLEANUP_AFTER_CONVERSION', 'false').lower() == 'true'

# Memory management settings
DEVICE_MAP = "auto"  # Use auto device map for memory efficiency

# Create a directory for downloaded models
MODELS_DIR = os.path.expanduser(os.getenv('MODELS_DIR', './downloaded_models'))
os.makedirs(MODELS_DIR, exist_ok=True)

# STEP 2: Clone llama.cpp (if not already installed)
LLAMA_CPP_DIR = os.path.expanduser(os.getenv('LLAMA_CPP_DIR', './llama.cpp'))
if not os.path.exists(LLAMA_CPP_DIR):
    print("Cloning llama.cpp...")
    try:
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp", LLAMA_CPP_DIR], check=True)
        subprocess.run(["make"], cwd=LLAMA_CPP_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during llama.cpp setup: {e}")
        print("Please make sure git is installed and you have the necessary build tools.")
        sys.exit(1)

# STEP 3: Install Dependencies (if not installed)
try:
    import torch
    import numpy
    import huggingface_hub
except ImportError:
    print("Installing missing dependencies...")
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Please try installing them manually with: pip install -r requirements.txt")
        sys.exit(1)

# Configure PyTorch to limit memory usage
print(f"Configuring memory limits (max {MAX_MEMORY_GB}GB)...")
torch.cuda.empty_cache()
gc.collect()

# Set PyTorch memory limits if CUDA is available
if torch.cuda.is_available():
    # Limit CUDA memory usage
    for i in range(torch.cuda.device_count()):
        device = torch.device(f'cuda:{i}')
        torch.cuda.set_per_process_memory_fraction(MAX_MEMORY_GB / 16, device)  # Assuming 16GB is max GPU memory
        print(f"Limited GPU {i} to {MAX_MEMORY_GB}GB")
else:
    print("CUDA not available, using CPU only")

# STEP 4: Download Hugging Face Model
# Extract model ID for local path
model_id = MODEL_NAME.split("/")[-1] if "/" in MODEL_NAME else MODEL_NAME
local_model_path = os.path.join(MODELS_DIR, model_id)

# Check if model is already downloaded to our local directory
if os.path.exists(local_model_path) and os.path.isdir(local_model_path):
    print(f"Model already downloaded to {local_model_path}. Using existing files.")
else:
    print(f"Downloading model {MODEL_NAME} to {local_model_path}...")
    try:
        # Load tokenizer first
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.save_pretrained(local_model_path)
        
        # Load model with memory-efficient settings
        print("Downloading model with memory-efficient settings...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map=DEVICE_MAP,  # Automatically distribute model across available devices
            torch_dtype=torch.float16,  # Use half precision to reduce memory usage
            low_cpu_mem_usage=True,  # Optimize for low CPU memory usage
        )
        
        # Save the model to local directory
        print(f"Saving model to {local_model_path}...")
        model.save_pretrained(local_model_path)
        
        # Force garbage collection to free up memory
        del model
        gc.collect()
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please check your internet connection and the model name.")
        sys.exit(1)

# STEP 5: Run Conversion Script
print("Converting model to GGUF format...")
# Find the correct conversion script
conversion_scripts = [
    os.path.join(LLAMA_CPP_DIR, "convert_hf_to_gguf.py"),  # Current name with underscores
    os.path.join(LLAMA_CPP_DIR, "convert-hf-to-gguf.py"),  # Old name with hyphens
]

convert_script = None
for script in conversion_scripts:
    if os.path.exists(script):
        convert_script = script
        break

if not convert_script:
    print("Error: Could not find the conversion script in the llama.cpp directory.")
    print("Please check if the llama.cpp repository was cloned correctly.")
    sys.exit(1)

print(f"Using conversion script: {convert_script}")

try:
    # Add memory-efficient flags to the conversion process
    # Use the local model path instead of the Hugging Face model ID
    subprocess.run([
        "python", convert_script, 
        local_model_path,  # Use local path instead of MODEL_NAME
        "--outtype", OUTPUT_TYPE,
        "--outfile", f"{model_id}.{OUTPUT_TYPE}.gguf"
    ], check=True, env={
        **os.environ,
        "PYTORCH_CUDA_ALLOC_CONF": f"max_split_size_mb:{MAX_MEMORY_GB * 1024 // 2}"  # Limit PyTorch memory allocation
    })
except subprocess.CalledProcessError as e:
    print(f"Error during model conversion: {e}")
    print("Please check the llama.cpp repository for updates or issues.")
    sys.exit(1)

print("✅ Conversion complete! Your GGUF model is ready.")

# STEP 6: Move Model to LM Studio Directory (Optional) with Model ID as the directory name
LM_STUDIO_DIR = os.path.expanduser(os.getenv('LM_STUDIO_DIR', '~/.lmstudio/models'))
LM_STUDIO_MODEL_DIR = os.path.join(LM_STUDIO_DIR, model_id)
if not os.path.exists(LM_STUDIO_MODEL_DIR):
    os.makedirs(LM_STUDIO_MODEL_DIR)

gguf_model_path = f"{model_id}.{OUTPUT_TYPE}.gguf"
if os.path.exists(gguf_model_path):
    print(f"Moving {gguf_model_path} to LM Studio directory...")
    try:
        subprocess.run(["mv", gguf_model_path, LM_STUDIO_MODEL_DIR], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error moving model to LM Studio directory: {e}")
        print(f"Your model is still available at: {gguf_model_path}")

# Clean up if enabled in .env
if CLEANUP_AFTER_CONVERSION:
    print("Cleaning up downloaded model files...")
    if os.path.exists(local_model_path):
        shutil.rmtree(local_model_path)

# Print the LM Studio model directory path
print(f"LM Studio model directory: {LM_STUDIO_MODEL_DIR}")

print("🚀 Done! You can now load the model in LM Studio.")