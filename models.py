# models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from loguru import logger
import os

# Fail fast if no GPU
if not torch.cuda.is_available():
    raise RuntimeError("❌ No GPU detected. NeurodivergentHelper requires CUDA for model loading.")

device = "cuda"

# Ordered candidate models (largest → smaller)
MODEL_CANDIDATES = [
    os.environ.get("MODEL_NAME"),  # user override via env var
    "meta-llama/Llama-3.2-70B-Instruct",
    "meta-llama/Llama-3.2-7B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",  # smallest, should always fit
]

# Globals
tokenizer, model, active_model_name = None, None, None


def try_load_model(name: str, quantize: bool = False):
    """Load a model from HF Hub. Optionally 4-bit quantization if VRAM limited."""
    tok = AutoTokenizer.from_pretrained(name, use_auth_token=os.environ.get("HF_TOKEN"))

    if quantize:
        logger.info(f"⚡ Loading {name} with 4-bit quantization...")
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        mdl = AutoModelForCausalLM.from_pretrained(
            name,
            quantization_config=quant_config,
            device_map="auto",
            trust_remote_code=True,
            use_auth_token=os.environ.get("HF_TOKEN")
        )
    else:
        logger.info(f"⚡ Loading {name} in half precision (fp16)...")
        mdl = AutoModelForCausalLM.from_pretrained(
            name,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            use_auth_token=os.environ.get("HF_TOKEN")
        )

    mdl.to(device)
    return tok, mdl


def load_model():
    """Try loading models in order. If OOM in fp16, retry in 4-bit."""
    global tokenizer, model, active_model_name

    if tokenizer and model:
        return tokenizer, model, active_model_name

    for candidate in MODEL_CANDIDATES:
        if not candidate:
            continue
        try:
            logger.info(f"🔎 Trying {candidate}...")
            tok, mdl = try_load_model(candidate, quantize=False)
            tokenizer, model, active_model_name = tok, mdl, candidate
            logger.success(f"✅ Loaded {candidate} in fp16")
            return tokenizer, model, active_model_name
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logger.warning(f"💾 OOM on {candidate} fp16. Retrying with 4-bit quantization...")
                try:
                    tok, mdl = try_load_model(candidate, quantize=True)
                    tokenizer, model, active_model_name = tok, mdl, candidate + " (4-bit)"
                    logger.success(f"✅ Loaded {candidate} in 4-bit quantization")
                    return tokenizer, model, active_model_name
                except Exception as e2:
                    logger.error(f"❌ Quantized load failed for {candidate}: {e2}")
            else:
                logger.error(f"❌ Failed to load {candidate}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to load {candidate}: {e}")

    raise RuntimeError("🚨 No GPU models could be loaded! Out of VRAM or missing files.")


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
