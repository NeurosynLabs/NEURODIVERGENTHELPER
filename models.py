import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger
import os

# --- Device setup ---
device = "cpu"
torch.set_num_threads(4)  # Adjust based on your CPU cores

# --- Model candidates ---
MODEL_CANDIDATES = [
    os.environ.get("MODEL_NAME"),  # optional user override
    "gemma3/gemma3-1b",           # CPU-friendly, high-quality conversational model
]

# --- Globals ---
tokenizer, model, active_model_name = None, None, None

def try_load_model(name: str):
    """Load a model from Hugging Face Hub optimized for CPU"""
    logger.info(f"⚡ Loading {name} on CPU...")

    tok = AutoTokenizer.from_pretrained(
        name,
        use_auth_token=os.environ.get("HF_TOKEN"),
        padding_side='left'
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    mdl = AutoModelForCausalLM.from_pretrained(
        name,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        use_auth_token=os.environ.get("HF_TOKEN")
    )
    mdl.to(device)
    mdl.eval()

    try:
        mdl = torch.jit.optimize_for_inference(mdl)
        logger.info("🚀 Applied JIT optimizations")
    except Exception as e:
        logger.warning(f"⚠️ JIT optimization failed: {e}")

    return tok, mdl

def load_model():
    """Load the first CPU-compatible model from candidates"""
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
            param_count = sum(p.numel() for p in mdl.parameters())
            logger.info(f"📊 Model has {param_count:,} parameters")
            return tokenizer, model, active_model_name
        except Exception as e:
            logger.error(f"❌ Failed to load {candidate}: {e}")

    raise RuntimeError("🚨 No CPU models could be loaded!")

def generate_response(prompt: str, max_length: int = 300, temperature: float = 0.6) -> str:
    """Generate a CPU-optimized, thoughtful response"""
    global tokenizer, model
    if not tokenizer or not model:
        load_model()

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.85,
                top_k=40,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )

        input_length = inputs['input_ids'].shape[1]
        generated_tokens = outputs[0][input_length:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        return response.strip()
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "I'm sorry, I encountered an issue generating a response."

def get_model_info():
    """Return model metadata"""
    global model, active_model_name, tokenizer
    if not model:
        return {"status": "No model loaded"}

    param_count = sum(p.numel() for p in model.parameters())
    vocab_size = tokenizer.vocab_size if tokenizer else "Unknown"

    return {
        "name": active_model_name,
        "parameters": f"{param_count:,}",
        "vocab_size": vocab_size,
        "device": device,
        "dtype": str(model.dtype) if hasattr(model, 'dtype') else "Unknown"
    }

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

def cleanup_model():
    """Clear loaded model and free memory"""
    global tokenizer, model, active_model_name
    if model:
        del model
    if tokenizer:
        del tokenizer
    tokenizer, model, active_model_name = None, None, None
    import gc
    gc.collect()
    logger.info("🧹 Model memory cleaned up")
