# models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger
import os

# CPU-only
device = "cpu"

# Candidate models (small CPU-friendly)
MODEL_CANDIDATES = [
    os.environ.get("MODEL_NAME"),  # optional user override
    "EleutherAI/gpt-neo-125M",    # small GPT-Neo, fast on CPU
    "distilgpt2",                  # very small GPT-2 variant
]

# Globals
tokenizer, model, active_model_name = None, None, None

def try_load_model(name: str):
    """Load a model from Hugging Face Hub on CPU"""
    logger.info(f"⚡ Loading {name} on CPU...")
    tok = AutoTokenizer.from_pretrained(name, use_auth_token=os.environ.get("HF_TOKEN"))
    mdl = AutoModelForCausalLM.from_pretrained(name)
    mdl.to(device)
    return tok, mdl

def load_model():
    """Try loading models in order until one works"""
    global tokenizer, model, active_model_name

    if tokenizer and model:
        return tokenizer, model, active_model_name

    for candidate in MODEL_CANDIDATES:
        if not candidate:
            continue
        try:
            tok, mdl = try_load_model(candidate)
            tokenizer, model, active_model_name = tok, mdl, candidate
            logger.success(f"✅ Loaded {candidate} on CPU")
            return tokenizer, model, active_model_name
        except Exception as e:
            logger.error(f"❌ Failed to load {candidate}: {e}")

    raise RuntimeError("🚨 No CPU models could be loaded!")

def get_tokenizer():
    global tokenizer
    if not tokenizer:
        load_model()
    return tokenizer

def get_model():
    global model
    if not model:
        load_model()
    return model

def get_active_model_name():
    global active_model_name
    return active_model_name or "Unknown"
