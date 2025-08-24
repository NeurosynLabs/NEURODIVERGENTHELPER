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
    context_text = "\n".join(SESSION_MEMORY[-5:])
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"

    inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")

    return {
        "response": response_text,
        "model_used": active_model
    }

# --- Gradio chat function ---
def gradio_chat(user_input, history):
    """Returns response and updated history"""
    SESSION_MEMORY.append(f"User: {user_input}")
    tokenizer, model, active_model = load_model()

    context_text = "\n".join(SESSION_MEMORY[-5:])
    full_prompt = f"{DEFAULT_PROMPT}\n\n{context_text}\nNeurodivergentHelper:"

    inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    SESSION_MEMORY.append(f"NeurodivergentHelper: {response_text}")
    history = history + [(user_input, response_text)]
    return history, history

# --- Launch Gradio UI if run directly ---
if __name__ == "__main__":
    with gr.Blocks() as demo:
        state = gr.State([])  # conversation history
        chatbot = gr.Chatbot()
        user_input = gr.Textbox(label="Your message", placeholder="Type your message here...")

        user_input.submit(
            gradio_chat,
            inputs=[user_input, state],
            outputs=[chatbot, state]
        )

    demo.launch(server_name="0.0.0.0", server_port=7860)
