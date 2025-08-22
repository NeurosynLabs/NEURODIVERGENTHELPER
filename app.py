# app.py
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import requests
import os
import threading
import uvicorn
import gradio as gr

# --- FastAPI setup ---
app = FastAPI(title="NeurodivergentHelper")

# --- Hugging Face ---
HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_NAME = "openai/gpt-oss-120b"
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Session memory ---
SESSION_MEMORY = []

# --- Load system prompt from GitHub ---
PROMPT_URL = "https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/prompt.txt"
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
response = requests.get(PROMPT_URL, headers=headers)
DEFAULT_PROMPT = response.text if response.status_code == 200 else "You are NeurodivergentHelper..."

# --- Lazy-load tokenizer & model ---
tokenizer, model = None, None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
        print("Loading model (this may take a while)...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float16 if device=="cuda" else torch.float32,
            use_auth_token=HF_TOKEN,
            trust_remote_code=True
        )
        model.to(device)
        print("✅ Model loaded successfully!")

# --- FastAPI endpoints ---
@app.get("/")
def root():
    return {"message": "NeurodivergentHelper API is live!"}

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("prompt", "")
    if not user_input:
        return {"error": "No prompt provided."}

    load_model()

    SESSION_MEMORY.append(f"User: {user_input}")
    context_text = "\n".join(SESSION_MEMORY[-5:])
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"

    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")

    return {"response": response_text}

# --- Gradio interface ---
def gradio_chat(user_input, history=[]):
    SESSION_MEMORY.append(f"User: {user_input}")
    load_model()
    context_text = "\n".join(SESSION_MEMORY[-5:])
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")
    history.append((user_input, response_text))
    return history, history

def launch_gradio():
    iface = gr.ChatInterface(
        gradio_chat,
        title="NeurodivergentHelper",
        description="Chat with your neurodivergent-friendly assistant.",
        allow_flagging="never"
    )
    iface.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8000)))

# --- Run FastAPI and Gradio concurrently ---
threading.Thread(target=launch_gradio, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
