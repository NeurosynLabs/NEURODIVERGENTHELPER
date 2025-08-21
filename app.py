from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pyngrok import ngrok
import os
import uvicorn

# --- Hugging Face Authentication ---
HF_TOKEN = os.getenv("HF_TOKEN", "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")
MODEL_NAME = "openai/gpt-oss-7b"

# --- Load Model and Tokenizer ---
print("Loading model... This may take a few minutes")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",          # Automatically choose GPU if available
    torch_dtype=torch.float16,  # Reduce VRAM usage
    use_auth_token=HF_TOKEN
)
print("Model loaded successfully.")

# --- Load Base Prompt ---
with open("/content/NeurodivergentHelper.txt", "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read()

# --- FastAPI App ---
app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.post("/query")
async def query(message: Message):
    prompt = f"{BASE_PROMPT}\nUser: {message.user_input}\nNeurodivergentHelper:"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=True,
        top_p=0.9,
        temperature=0.8
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.replace(BASE_PROMPT, "").strip()
    return {"response": response}

# --- Start ngrok Tunnel ---
public_url = ngrok.connect(8000)
print("Public URL:", public_url)

# --- Run FastAPI ---
uvicorn.run(app, host="0.0.0.0", port=8000)
