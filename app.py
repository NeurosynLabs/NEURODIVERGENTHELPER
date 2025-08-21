# app.py

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Hugging Face token from environment variable
import os
HF_TOKEN = os.getenv("HF_TOKEN")

# Model & tokenizer
MODEL_NAME = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", use_auth_token=HF_TOKEN)

# Load NeurodivergentHelper prompt dynamically from GitHub
PROMPT_URL = "https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper/NeurodivergentHelper.txt"
BASE_PROMPT = requests.get(PROMPT_URL).text

# FastAPI app
app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.post("/query")
async def query(message: Message):
    prompt = f"{BASE_PROMPT}\nUser: {message.user_input}\nNeurodivergentHelper:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove prompt echo
    response = response.replace(BASE_PROMPT, "").strip()
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
