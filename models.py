import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import yaml

# --- Configuration ---
DEFAULT_MODEL_NAME = "NousResearch/Nous-Hermes-CPU"  # CPU-friendly
MAX_HISTORY = 5

# Cache to avoid reloading models
_model_cache = {}

# --- Load SYSTEM_PROMPT from YAML ---
PROMPT_FILE = os.environ.get("PROMPT_URL", "NeurodivergentHelper.prompt.yml")

try:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_data = yaml.safe_load(f)
        SYSTEM_PROMPT = prompt_data["messages"][0]["content"]
except Exception as e:
    SYSTEM_PROMPT = "You are NeurodivergentHelper..."
    print(f"Warning: Failed to load YAML prompt. Using default SYSTEM_PROMPT. Error: {e}")


def get_device():
    """Choose GPU if available, else CPU."""
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
    """Returns the currently loaded model name."""
    return list(_model_cache.keys())[0] if _model_cache else DEFAULT_MODEL_NAME


def get_tokenizer(model_name=None):
    return load_model(model_name)[0]


def get_model(model_name=None):
    return load_model(model_name)[1]
