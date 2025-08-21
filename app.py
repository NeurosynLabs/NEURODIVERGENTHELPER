# app.py
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import requests

app = FastAPI(title="NeurodivergentHelper")

# Hugging Face authentication
HF_TOKEN = "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"  # your read-only token
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Load model and tokenizer (non-gated, GPU-compatible example)
MODEL_NAME = "TheBloke/GPT-OSS-6B-GGUF"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", use_auth_token=HF_TOKEN)
model.to(device)

# Load system prompt from GitHub
PROMPT_URL = "https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/prompt.txt"
response = requests.get(PROMPT_URL, headers=headers)
DEFAULT_PROMPT = response.text if response.status_code == 200 else "You are NeurodivergentHelper..."

@app.get("/")
def root():
    return {"message": "NeurodivergentHelper API is live!"}

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("prompt", "")

    if not user_input:
        return {"error": "No prompt provided."}

    full_prompt = f"{DEFAULT_PROMPT}\n\nUser: {user_input}\nNeurodivergentHelper:"

    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"response": response_text}
