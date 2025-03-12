import os
import subprocess
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer

# STEP 1: Set Model Name and Output Type
MODEL_NAME = "MACLAB-HFUT/PsycoLLM"  # Change this to the model you want
OUTPUT_TYPE = "f16"  # Options: f16, q4_0, q4_K_M, q8_0, etc.

# STEP 2: Clone llama.cpp (if not already installed)
if not os.path.exists("llama.cpp"):
    print("Cloning llama.cpp...")
    try:
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp"], check=True)
        subprocess.run(["make"], cwd="llama.cpp", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during llama.cpp setup: {e}")
        print("Please make sure git is installed and you have the necessary build tools.")
        sys.exit(1)

# STEP 3: Install Dependencies (if not installed)
try:
    import torch
    import numpy
except ImportError:
    print("Installing missing dependencies...")
    try:
        subprocess.run(["pip", "install", "torch", "numpy", "sentencepiece", "transformers"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Please try installing them manually with: pip install -r requirements.txt")
        sys.exit(1)

# STEP 4: Download Hugging Face Model
print(f"Downloading model: {MODEL_NAME}")
try:
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
except Exception as e:
    print(f"Error downloading model: {e}")
    print("Please check your internet connection and the model name.")
    sys.exit(1)

# STEP 5: Run Conversion Script
print("Converting model to GGUF format...")
convert_script = os.path.join("llama.cpp", "convert-hf-to-gguf.py")
try:
    subprocess.run(["python", convert_script, MODEL_NAME, "--outtype", OUTPUT_TYPE], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error during model conversion: {e}")
    print("Please check the llama.cpp repository for updates or issues.")
    sys.exit(1)

print("✅ Conversion complete! Your GGUF model is ready.")

# STEP 6: Move Model to LM Studio Directory (Optional)
LM_STUDIO_MODEL_DIR = os.path.expanduser("~/LMStudio/models/")
if not os.path.exists(LM_STUDIO_MODEL_DIR):
    os.makedirs(LM_STUDIO_MODEL_DIR)

gguf_model_path = f"{MODEL_NAME.split('/')[-1]}.{OUTPUT_TYPE}.gguf"
if os.path.exists(gguf_model_path):
    print(f"Moving {gguf_model_path} to LM Studio directory...")
    try:
        subprocess.run(["mv", gguf_model_path, LM_STUDIO_MODEL_DIR], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error moving model to LM Studio directory: {e}")
        print(f"Your model is still available at: {gguf_model_path}")

print("🚀 Done! You can now load the model in LM Studio.")