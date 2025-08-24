from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import json
from typing import List, Dict
import asyncio
import gradio as gr
from models import load_model, get_tokenizer, get_model, get_active_model_name

# --- FastAPI setup ---
app = FastAPI(title="NeurodivergentHelper")

# Add CORS middleware for iframe embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load system prompt ---
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "NeurodivergentHelper.prompt.yml")
import yaml
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    yaml_data = yaml.safe_load(f)
DEFAULT_PROMPT = ""
for msg in yaml_data.get("messages", []):
    if msg.get("role") == "system":
        DEFAULT_PROMPT = msg.get("content", "").strip()
        break
if not DEFAULT_PROMPT:
    DEFAULT_PROMPT = "You are NeurodivergentHelper, a compassionate AI companion."

# --- Session storage ---
sessions: Dict[str, List[Dict]] = {}

def get_session_id(request: Request) -> str:
    return request.client.host + str(hash(request.headers.get("user-agent", "")))

def add_to_session(session_id: str, role: str, content: str, max_history: int = 10):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})
    if len(sessions[session_id]) > max_history:
        sessions[session_id] = sessions[session_id][-max_history:]

def get_session_context(session_id: str) -> str:
    if session_id not in sessions:
        return ""
    context_parts = []
    for msg in sessions[session_id][-5:]:
        if msg["role"] == "user":
            context_parts.append(f"User: {msg['content']}")
        else:
            context_parts.append(f"NeurodivergentHelper: {msg['content']}")
    return "\n".join(context_parts)

# --- API Root ---
@app.get("/")
def root():
    return {"message": "NeurodivergentHelper API is live!", "model": get_active_model_name(), "version": "1.0.0"}

# --- Embed Interface (ChatGPT-like web UI) ---
@app.get("/embed", response_class=HTMLResponse)
def embed_interface():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeurodivergentHelper Chat</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .chat-container { max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }
            .messages { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; border-radius: 8px; background: #fafafa; }
            .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 15px; max-width: 80%; }
            .user-message { background: #007bff; color: white; margin-left: auto; text-align: right; }
            .bot-message { background: #e9ecef; color: #333; }
            .input-area { display: flex; gap: 10px; }
            #user-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; }
            #send-btn, #clear-btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 20px; cursor: pointer; }
            #clear-btn { background: #6c757d; }
            #send-btn:disabled { background: #ccc; cursor: default; }
            .accordion { background: #007bff; color: white; cursor: pointer; padding: 10px; width: 100%; text-align: left; border: none; outline: none; border-radius: 8px; margin-bottom: 10px; }
            .panel { padding: 0 10px; display: none; background-color: #f1f1f1; overflow: hidden; border-radius: 8px; margin-bottom: 10px; }
            .panel input, .panel select { width: 100%; padding: 8px; margin: 5px 0; border-radius: 8px; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h2>NeurodivergentHelper</h2>
            <div class="messages" id="messages"></div>
            
            <button class="accordion">User Settings</button>
            <div class="panel">
                <input type="text" id="nickname" placeholder="Nickname">
                <select id="tone">
                    <option value="patient">Patient</option>
                    <option value="concise">Concise</option>
                    <option value="playful">Playful</option>
                    <option value="detailed">Detailed</option>
                </select>
                <input type="text" id="topics" placeholder="Topics of interest">
            </div>
            
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Type your message here..." />
                <button id="send-btn">Send</button>
                <button id="clear-btn">Clear</button>
            </div>
        </div>
        
        <script>
            const messages = document.getElementById('messages');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const clearBtn = document.getElementById('clear-btn');
            const accordion = document.querySelector(".accordion");
            const panel = document.querySelector(".panel");
            
            accordion.addEventListener("click", () => { panel.style.display = panel.style.display === "block" ? "none" : "block"; });

            function addMessage(content, isUser=false) {
                const div = document.createElement('div');
                div.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                div.textContent = content;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }

            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                addMessage(message, true);
                userInput.value = '';
                sendBtn.disabled = true;
                sendBtn.textContent = 'Thinking...';

                const settings = {
                    nickname: document.getElementById('nickname').value || 'User',
                    tone: document.getElementById('tone').value,
                    topics: document.getElementById('topics').value
                };

                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: message, settings })
                    });
                    const data = await response.json();
                    if (data.response) addMessage(data.response);
                    else addMessage('Error: could not get response.');
                } catch (e) { addMessage('Error: connection issue.'); }

                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                userInput.focus();
            }

            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });
            clearBtn.addEventListener('click', () => { messages.innerHTML=''; });

            addMessage("Hello! I'm NeurodivergentHelper. How can I support you today?");
            userInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Query endpoint ---
@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("prompt", "").strip()
    settings = data.get("settings", {})

    if not user_input:
        return {"error": "No prompt provided."}

    session_id = get_session_id(request)
    add_to_session(session_id, "user", user_input)

    tokenizer, model, active_model = load_model()
    context = get_session_context(session_id)
    nickname = settings.get("nickname", "User")
    tone = settings.get("tone", "patient")
    topics = settings.get("topics", "")

    full_prompt = f"{DEFAULT_PROMPT}\n\nUser: {nickname}\nTone: {tone}\nTopics: {topics}\n{context}\nUser: {user_input}\nNeurodivergentHelper:"

    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True, pad_token_id=tokenizer.eos_token_id)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        add_to_session(session_id, "assistant", response_text)
        return {"response": response_text, "model_used": active_model, "session_id": session_id}
    except Exception as e:
        return {"error": f"Generation failed: {e}"}

# --- Gradio UI (optional alternative) ---
def gradio_chat(user_input, history):
    if not user_input.strip():
        return history, history
    try:
        tokenizer, model, _ = load_model()
        context_parts = []
        for exchange in history[-3:]:
            context_parts.append(f"User: {exchange[0]}")
            context_parts.append(f"NeurodivergentHelper: {exchange[1]}")
        context = "\n".join(context_parts)
        full_prompt = f"{DEFAULT_PROMPT}\n\n{context}\nUser: {
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os, json, asyncio, gc
import gradio as gr
from models import load_model, get_tokenizer, get_model, get_active_model_name

app = FastAPI(title="NeurodivergentHelper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load prompt ---
PROMPT_FILE = "NeurodivergentHelper.prompt.yml"
import yaml
with open(PROMPT_FILE, "r") as f:
    yaml_data = yaml.safe_load(f)
    SYSTEM_PROMPT = ""
    if 'messages' in yaml_data:
        for msg in yaml_data['messages']:
            if msg.get('role') == "system":
                SYSTEM_PROMPT = msg.get('content', '').strip()

# --- Session storage ---
sessions = {}

def get_session_id(request: Request) -> str:
    return request.client.host + str(hash(request.headers.get("user-agent", "")))

def add_to_session(session_id: str, role: str, content: str, max_history: int = 10):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})
    if len(sessions[session_id]) > max_history:
        sessions[session_id] = sessions[session_id][-max_history:]

def get_session_context(session_id: str) -> str:
    if session_id not in sessions: return ""
    context_parts = []
    for msg in sessions[session_id][-5:]:
        prefix = "User: " if msg["role"] == "user" else "NeurodivergentHelper: "
        context_parts.append(f"{prefix}{msg['content']}")
    return "\n".join(context_parts)

# --- FastAPI Endpoints ---
@app.get("/")
def root():
    return {"message": "NeurodivergentHelper API is live!", "model": get_active_model_name(), "version": "1.0.0"}

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("prompt", "").strip()
    settings = data.get("settings", {})
    if not user_input:
        return JSONResponse({"error": "No prompt provided."})
    session_id = get_session_id(request)
    add_to_session(session_id, "user", user_input)
    tokenizer, model, active_model = load_model()
    context = get_session_context(session_id)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\nUser: {user_input}\nNeurodivergentHelper:"
    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True, pad_token_id=tokenizer.eos_token_id)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        add_to_session(session_id, "assistant", response_text)
        return {"response": response_text, "model_used": active_model, "session_id": session_id}
    except Exception as e:
        return {"error": f"Failed to generate response: {e}"}

@app.get("/embed", response_class=HTMLResponse)
def embed_interface():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeurodivergentHelper Chat</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .chat-container { max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }
            .messages { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; border-radius: 8px; background: #fafafa; }
            .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 15px; max-width: 80%; }
            .user-message { background: #007bff; color: white; margin-left: auto; text-align: right; }
            .bot-message { background: #e9ecef; color: #333; }
            .input-area { display: flex; gap: 10px; }
            #user-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; }
            #send-btn, #clear-btn { padding: 10px 20px; border: none; border-radius: 20px; cursor: pointer; }
            #send-btn { background: #007bff; color: white; }
            #clear-btn { background: #6c757d; color: white; }
            #send-btn:disabled { background: #ccc; cursor: default; }
            .accordion { background: #007bff; color: white; cursor: pointer; padding: 10px; width: 100%; text-align: left; border: none; outline: none; border-radius: 8px; margin-bottom: 10px; }
            .panel { padding: 0 10px; display: none; background-color: #f1f1f1; overflow: hidden; border-radius: 8px; margin-bottom: 10px; }
            .panel input, .panel select { width: 100%; padding: 8px; margin: 5px 0; border-radius: 8px; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h2>NeurodivergentHelper</h2>
            <div class="messages" id="messages"></div>
            
            <button class="accordion">User Settings</button>
            <div class="panel">
                <input type="text" id="nickname" placeholder="Nickname">
                <select id="tone">
                    <option value="patient">Patient</option>
                    <option value="concise">Concise</option>
                    <option value="playful">Playful</option>
                    <option value="detailed">Detailed</option>
                </select>
                <input type="text" id="topics" placeholder="Topics of interest">
            </div>
            
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Type your message here..." />
                <button id="send-btn">Send</button>
                <button id="clear-btn">Clear</button>
            </div>
        </div>
        
        <script>
            const messages = document.getElementById('messages');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const clearBtn = document.getElementById('clear-btn');
            const accordion = document.querySelector(".accordion");
            const panel = document.querySelector(".panel");
            
            accordion.addEventListener("click", () => { panel.style.display = panel.style.display === "block" ? "none" : "block"; });

            function addMessage(content, isUser=false) {
                const div = document.createElement('div');
                div.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                div.textContent = content;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }

            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                addMessage(message, true);
                userInput.value = '';
                sendBtn.disabled = true;
                sendBtn.textContent = 'Thinking...';
                const settings = { nickname: document.getElementById('nickname').value, tone: document.getElementById('tone').value, topics: document.getElementById('topics').value };
                try {
                    const response = await fetch('/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: message, settings }) });
                    const data = await response.json();
                    addMessage(data.response || 'Error: No response.');
                } catch (e) { addMessage('Error: connection issue.'); }
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                userInput.focus();
            }

            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', e => { if(e.key==='Enter') sendMessage(); });
            clearBtn.addEventListener('click', () => { messages.innerHTML=''; });
            addMessage("Hello! I'm NeurodivergentHelper. How can I support you today?");
            userInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Gradio interface ---
def gradio_chat(user_input, history):
    if not user_input.strip(): return history, history
    tokenizer, model, active_model = load_model()
    context_parts = []
    for exchange in history[-3:]:
        context_parts.append(f"User: {exchange[0]}")
        context_parts.append(f"NeurodivergentHelper: {exchange[1]}")
    full_prompt = f"{SYSTEM_PROMPT}\n\n{'\n'.join(context_parts)}\nUser: {user_input}\nNeurodivergentHelper:"
    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True, pad_token_id=tokenizer.eos_token_id)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        history.append([user_input, response_text])
        return history, history
    except:
        error_response = "Error generating response."
        history.append([user_input, error_response])
        return history, history

gradio_interface = gr.Blocks()
with gradio_interface:
    with gr.Row():
        chatbot = gr.Chatbot()
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Type your message here...")
        submit_btn = gr.Button("Send")
    submit_btn.click(gradio_chat, inputs=[txt, chatbot], outputs=[chatbot, chatbot])
    txt.submit(gradio_chat, inputs=[txt, chatbot], outputs=[chatbot, chatbot])

@app.get("/gradio", response_class=HTMLResponse)
def gradio_app():
    return HTMLResponse(gradio_interface.launch(share=False, inline=True)[0])
