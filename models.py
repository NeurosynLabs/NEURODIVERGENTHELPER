# models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger
import os

device = "cpu"  # CPU-only

# Ordered candidate models (small models only for CPU)
MODEL_CANDIDATES = [
    os.environ.get("MODEL_NAME"),  # user override via env var
    "EleutherAI/gpt-neo-125M",    # small CPU-friendly model
    "distilgpt2",                  # smallest GPT-2 variant
]

# Globals
tokenizer, model, active_model_name = None, None, None

def try_load_model(name: str):
    """Load a model from HF Hub on CPU"""
    logger.info(f"⚡ Loading {name} on CPU...")
    tok = AutoTokenizer.from_pretrained(name, use_auth_token=os.environ.get("HF_TOKEN"))
    mdl = AutoModelForCausalLM.from_pretrained(name)
    mdl.to(device)
    return tok, mdl

def load_model():
    """Try loading models in order"""
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
