# app.py
from fastapi import FastAPI, Request
import requests
import os
import gradio as gr
from models import load_model, get_tokenizer, get_model, get_active_model_name

# --- FastAPI setup ---
app = FastAPI(title="NeurodivergentHelper")

# --- Hugging Face token & system prompt ---
HF_TOKEN = os.environ.get("HF_TOKEN", "")
PROMPT_URL = os.environ.get(
    "PROMPT_URL",
    "https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper.txt"
)
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
with requests.get(PROMPT_URL, headers=headers) as response:
    DEFAULT_PROMPT = response.text if response.status_code == 200 else "You are NeurodivergentHelper..."

# --- Session memory ---
SESSION_MEMORY = []


@app.get("/")
def root():
    """API root: returns live message and active model"""
    return {
        "message": "NeurodivergentHelper API is live!",
        "model": get_active_model_name()
    }


@app.post("/query")
async def query(request: Request):
    """Query endpoint: returns generated response and model used"""
    data = await request.json()
    user_input = data.get("prompt", "")
    if not user_input:
        return {"error": "No prompt provided."}

    tokenizer, model, active_model = load_model()

    SESSION_MEMORY.append(f"User: {user_input}")
    context_text = "\n".join(SESSION_MEMORY[-5:])  # last 5 entries for context
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"

    # CPU-friendly tokenizer call with truncation
    inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")

    return {
        "response": response_text,
        "model_used": active_model
    }


# --- Gradio interface ---
def gradio_chat(user_input, history=[]):
    """Gradio chat function"""
    SESSION_MEMORY.append(f"User: {user_input}")
    tokenizer, model, active_model = load_model()

    context_text = "\n".join(SESSION_MEMORY[-5:])
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"

    # CPU-friendly tokenizer call with truncation
    inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")
    history = history + [(user_input, response_text)]
    return response_text, history


# --- Optional: Launch Gradio UI if run directly ---
if __name__ == "__main__":
    import uvicorn
    interface = gr.Interface(
        fn=gradio_chat,
        inputs="text",
        outputs=["text", "state"],
        title="NeurodivergentHelper",
        description="Ask questions and get AI responses (CPU-only)"
    )
    interface.launch(server_name="0.0.0.0", server_port=7860)
    # Or if you prefer FastAPI:
    # uvicorn.run(app, host="0.0.0.0", port=8000)
