from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os, json, asyncio, gc
from models import load_model, get_active_model_name, DEFAULT_MODEL_NAME

# --- FastAPI setup ---
app = FastAPI(title="NeurodivergentHelper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if session_id not in sessions:
        return ""
    context_parts = []
    for msg in sessions[session_id][-5:]:
        prefix = "User: " if msg["role"] == "user" else "NeurodivergentHelper: "
        context_parts.append(f"{prefix}{msg['content']}")
    return "\n".join(context_parts)

# --- API Root ---
@app.get("/")
def root():
    return {
        "message": "NeurodivergentHelper API is live!",
        "model": get_active_model_name(),
        "version": "1.0.0"
    }

# --- Query Endpoint ---
@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("prompt", "").strip()
    settings = data.get("settings", {})
    model_name = settings.get("model_name", DEFAULT_MODEL_NAME)

    if not user_input:
        return JSONResponse({"error": "No prompt provided."})

    session_id = get_session_id(request)
    add_to_session(session_id, "user", user_input)

    tokenizer, model, active_model = load_model(model_name)
    context = get_session_context(session_id)
    nickname = settings.get("nickname", "User")
    tone = settings.get("tone", "patient")
    topics = settings.get("topics", "")

    SYSTEM_PROMPT = (
        "You are NeurodivergentHelper—an advanced emotional intelligence and "
        "linguistic support system purpose-built for neurodivergent individuals. "
        "Respond compassionately and informatively."
    )

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\nUser: {nickname}\nTone: {tone}\nTopics: {topics}\n"
        f"{context}\nUser: {user_input}\nNeurodivergentHelper:"
    )

    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        add_to_session(session_id, "assistant", response_text)
        return {"response": response_text, "model_used": active_model, "session_id": session_id}
    except Exception as e:
        return JSONResponse({"error": f"Failed to generate response: {e}"})

# --- Embed Interface with Model Selector ---
@app.get("/embed", response_class=HTMLResponse)
def embed_interface():
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>NeurodivergentHelper Chat</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{ font-family: Arial, sans-serif; margin:0; padding:20px; background:#f5f5f5; }}
.chat-container {{ max-width:700px; margin:0 auto; background:white; border-radius:12px; padding:20px; box-shadow:0 4px 15px rgba(0,0,0,0.15); }}
.messages {{ height:400px; overflow-y:auto; border:1px solid #ddd; padding:10px; margin-bottom:20px; border-radius:8px; background:#fafafa; }}
.message {{ margin-bottom:10px; padding:8px 12px; border-radius:15px; max-width:80%; }}
.user-message {{ background:#007bff; color:white; margin-left:auto; text-align:right; }}
.bot-message {{ background:#e9ecef; color:#333; }}
.input-area {{ display:flex; gap:10px; }}
#user-input {{ flex:1; padding:10px; border:1px solid #ddd; border-radius:20px; }}
#send-btn, #clear-btn {{ padding:10px 20px; border:none; border-radius:20px; cursor:pointer; }}
#send-btn {{ background:#007bff; color:white; }}
#clear-btn {{ background:#6c757d; color:white; }}
#send-btn:disabled {{ background:#ccc; cursor:default; }}
.accordion {{ background:#007bff; color:white; cursor:pointer; padding:10px; width:100%; text-align:left; border:none; outline:none; border-radius:8px; margin-bottom:10px; }}
.panel {{ padding:0 10px; display:none; background-color:#f1f1f1; overflow:hidden; border-radius:8px; margin-bottom:10px; }}
.panel input, .panel select {{ width:100%; padding:8px; margin:5px 0; border-radius:8px; border:1px solid #ccc; }}
</style>
</head>
<body>
<div class="chat-container">
<h2>NeurodivergentHelper</h2>
<div class="messages" id="messages"></div>
<button class="accordion">User Settings & Model</button>
<div class="panel">
<input type="text" id="nickname" placeholder="Nickname">
<select id="tone">
<option value="patient">Patient</option>
<option value="concise">Concise</option>
<option value="playful">Playful</option>
<option value="detailed">Detailed</option>
</select>
<input type="text" id="topics" placeholder="Topics of interest">
<select id="model_name">
<option value="{DEFAULT_MODEL_NAME}">{DEFAULT_MODEL_NAME}</option>
<!-- Add other models here if desired -->
</select>
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

accordion.addEventListener("click", () => {{ panel.style.display = panel.style.display === "block" ? "none" : "block"; }});

function addMessage(content, isUser=false) {{
    const div = document.createElement('div');
    div.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
    div.textContent = content;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}}

async function sendMessage() {{
    const message = userInput.value.trim();
    if (!message) return;
    addMessage(message, true);
    userInput.value = '';
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';
    const settings = {{
        nickname: document.getElementById('nickname').value,
        tone: document.getElementById('tone').value,
        topics: document.getElementById('topics').value,
        model_name: document.getElementById('model_name').value
    }};
    try {{
        const response = await fetch('/query', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ prompt: message, settings }}) }});
        const data = await response.json();
        addMessage(data.response || 'Error: No response.');
    }} catch (e) {{ addMessage('Error: connection issue.'); }}
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
    userInput.focus();
}}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', e => {{ if(e.key==='Enter') sendMessage(); }});
clearBtn.addEventListener('click', () => {{ messages.innerHTML=''; }});
addMessage("Hello! I'm NeurodivergentHelper. How can I support you today?");
userInput.focus();
</script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
