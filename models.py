# models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# --- Configuration ---
# Default CPU-optimized model
DEFAULT_MODEL_NAME = "NousResearch/Nous-Hermes-CPU"  # CPU-friendly
MAX_HISTORY = 5

# Store loaded models in a cache to avoid reloading
_model_cache = {}

def get_device():
    """
    Determines device: CPU by default, GPU if available.
    """
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model_name=None):
    """
    Loads model and tokenizer. Returns (tokenizer, model, model_name)
    """
    model_name = model_name or DEFAULT_MODEL_NAME
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
    """
    Returns the currently loaded model name.
    """
    return list(_model_cache.keys())[0] if _model_cache else DEFAULT_MODEL_NAME

def get_tokenizer(model_name=None):
    """
    Returns tokenizer only.
    """
    return load_model(model_name)[0]

def get_model(model_name=None):
    """
    Returns model only.
    """
    return load_model(model_name)[1]

