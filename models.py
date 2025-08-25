import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import yaml

# --- Load configuration from YAML ---
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "NeurodivergentHelper.prompt.yml")
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    yaml_data = yaml.safe_load(f)

# System prompt
SYSTEM_PROMPT = ""
for msg in yaml_data.get("messages", []):
    if msg.get("role") == "system":
        SYSTEM_PROMPT = msg.get("content", "").strip()
        break

# Suggested model (from YAML, optional)
SUGGESTED_MODEL = yaml_data.get("model", None)

# --- Hardware-aware default ---
CPU_FRIENDLY_MODEL = "NousResearch/Nous-Hermes-CPU"  # Works on all CPUs
GPU_FRIENDLY_MODEL = "NousResearch/Nous-Hermes-7B"   # Larger, GPU recommended

MAX_HISTORY = 5
_model_cache = {}

def get_device():
    """Detect available device. Defaults to CPU if GPU not usable."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

def select_model():
    """Choose model based on hardware and YAML suggestion."""
    device = get_device()
    if device.type == "cuda":
        # Use GPU-friendly model if GPU exists
        return GPU_FRIENDLY_MODEL
    else:
        # Use YAML suggestion if compatible, else CPU-friendly
        if SUGGESTED_MODEL:
            return SUGGESTED_MODEL
        return CPU_FRIENDLY_MODEL

def load_model(model_name=None):
    """Load tokenizer and model, caching for reuse."""
    model_name = model_name or select_model()
    if model_name in _model_cache:
        return _model_cache[model_name]

    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.to(device)
    model.eval()

    _model_cache[model_name] = (tokenizer, model, model_name)
    return tokenizer, model, model_name

def get_active_model_name():
    return list(_model_cache.keys())[0] if _model_cache else select_model()

def get_tokenizer(model_name=None):
    return load_model(model_name)[0]

def get_model(model_name=None):
    return load_model(model_name)[1]
