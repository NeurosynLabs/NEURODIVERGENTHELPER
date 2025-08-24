# models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger
import os

# CPU-only with optimization
device = "cpu"
torch.set_num_threads(4)  # Adjust based on your CPU cores

# Enhanced model candidates with better CPU performers
MODEL_CANDIDATES = [
    os.environ.get("MODEL_NAME"),  # optional user override
    "microsoft/DialoGPT-small",    # optimized for conversation
    "EleutherAI/gpt-neo-125M",     # small GPT-Neo, fast on CPU
    "distilgpt2",                  # very small GPT-2 variant
    "microsoft/DialoGPT-medium",   # fallback if you need better quality
]

# Globals
tokenizer, model, active_model_name = None, None, None

def try_load_model(name: str):
    """Load a model from Hugging Face Hub on CPU with optimizations"""
    logger.info(f"⚡ Loading {name} on CPU...")
    
    # Load tokenizer with padding token fix
    tok = AutoTokenizer.from_pretrained(
        name, 
        use_auth_token=os.environ.get("HF_TOKEN"),
        padding_side='left'  # Better for generation
    )
    
    # Add pad token if missing (common issue)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    
    # Load model with CPU optimizations
    mdl = AutoModelForCausalLM.from_pretrained(
        name,
        torch_dtype=torch.float32,  # Explicit CPU dtype
        low_cpu_mem_usage=True,     # Memory optimization
        use_auth_token=os.environ.get("HF_TOKEN")
    )
    
    # Move to CPU and optimize
    mdl.to(device)
    mdl.eval()  # Set to evaluation mode
    
    # Enable CPU optimizations if available
    try:
        mdl = torch.jit.optimize_for_inference(mdl)
        logger.info("🚀 Applied JIT optimizations")
    except Exception as e:
        logger.warning(f"⚠️ JIT optimization failed: {e}")
    
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
            
            # Log model info
            param_count = sum(p.numel() for p in mdl.parameters())
            logger.info(f"📊 Model has {param_count:,} parameters")
            
            return tokenizer, model, active_model_name
        except Exception as e:
            logger.error(f"❌ Failed to load {candidate}: {e}")

    raise RuntimeError("🚨 No CPU models could be loaded!")

def generate_response(prompt: str, max_length: int = 200, temperature: float = 0.7) -> str:
    """Optimized generation function"""
    global tokenizer, model
    
    if not tokenizer or not model:
        load_model()
    
    try:
        # Tokenize with proper truncation for long prompts
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,  # Adjust based on model's context window
            padding=True
        ).to(device)
        
        # Generate with optimized parameters
        with torch.no_grad():  # Disable gradient computation for inference
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Decode only the new tokens
        input_length = inputs['input_ids'].shape[1]
        generated_tokens = outputs[0][input_length:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "I'm sorry, I encountered an issue generating a response."

def get_model_info():
    """Get detailed model information"""
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

# Memory cleanup function
def cleanup_model():
    """Free up memory by clearing loaded model"""
    global tokenizer, model, active_model_name
    
    if model:
        del model
    if tokenizer:
        del tokenizer
    
    tokenizer, model, active_model_name = None, None, None
    
    # Force garbage collection
    import gc
    gc.collect()
    
    logger.info("🧹 Model memory cleaned up")
