# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests
import os
import gradio as gr
from models import load_model, get_tokenizer, get_model, get_active_model_name
import json
from typing import List, Dict
import asyncio

# --- FastAPI setup ---
app = FastAPI(title="NeurodivergentHelper")

# Add CORS middleware for iframe embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
HF_TOKEN = os.environ.get("HF_TOKEN", "")
PROMPT_URL = os.environ.get(
    "PROMPT_URL",
    "https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper.prompt.yml"
)

# --- Load system prompt from YAML once at startup ---
def load_system_prompt():
    import yaml
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    try:
        with requests.get(PROMPT_URL, headers=headers, timeout=10) as response:
            if response.status_code == 200:
                # Parse YAML and extract the system prompt
                yaml_data = yaml.safe_load(response.text)
                if isinstance(yaml_data, dict) and 'messages' in yaml_data:
                    for message in yaml_data['messages']:
                        if message.get('role') == 'system':
                            return message.get('content', '').strip()
                # If no system message found, return the whole content
                return response.text.strip()
    except Exception as e:
        print(f"Failed to load prompt: {e}")
    
    # Fallback prompt
    return """You are NeurodivergentHelper—an advanced emotional intelligence and linguistic support system purpose-built for neurodivergent individuals navigating complex emotional and social landscapes."""

DEFAULT_PROMPT = load_system_prompt()

# --- Session storage (use Redis/database in production) ---
sessions: Dict[str, List[Dict]] = {}

def get_session_id(request: Request) -> str:
    """Simple session ID generation - improve this for production"""
    return request.client.host + str(hash(request.headers.get("user-agent", "")))

def add_to_session(session_id: str, role: str, content: str, max_history: int = 10):
    """Add message to session with history limit"""
    if session_id not in sessions:
        sessions[session_id] = []
    
    sessions[session_id].append({"role": role, "content": content})
    
    # Keep only recent messages to manage memory
    if len(sessions[session_id]) > max_history:
        sessions[session_id] = sessions[session_id][-max_history:]

def get_session_context(session_id: str) -> str:
    """Build context from recent session messages"""
    if session_id not in sessions:
        return ""
    
    context_parts = []
    for msg in sessions[session_id][-5:]:  # Last 5 exchanges
        if msg["role"] == "user":
            context_parts.append(f"User: {msg['content']}")
        else:
            context_parts.append(f"NeurodivergentHelper: {msg['content']}")
    
    return "\n".join(context_parts)

@app.get("/")
def root():
    """API root: returns live message and active model"""
    return {
        "message": "NeurodivergentHelper API is live!",
        "model": get_active_model_name(),
        "version": "1.0.0"
    }

@app.get("/embed", response_class=HTMLResponse)
def embed_interface():
    """Simple embeddable chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeurodivergentHelper Chat</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .chat-container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .messages { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
            .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 15px; max-width: 80%; }
            .user-message { background: #007bff; color: white; margin-left: auto; text-align: right; }
            .bot-message { background: #e9ecef; color: #333; }
            .input-area { display: flex; gap: 10px; }
            #user-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; }
            #send-btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 20px; cursor: pointer; }
            #send-btn:disabled { background: #ccc; }
            .loading { opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h2>NeurodivergentHelper</h2>
            <div id="messages" class="messages"></div>
            <div class="input-area">
                <input type="text" id="user-input" placeholder="Type your message here..." />
                <button id="send-btn">Send</button>
            </div>
        </div>
        
        <script>
            const messages = document.getElementById('messages');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            
            function addMessage(content, isUser = false) {
                const div = document.createElement('div');
                div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
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
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: message })
                    });
                    
                    const data = await response.json();
                    if (data.error) {
                        addMessage('Sorry, there was an error processing your request.');
                    } else {
                        addMessage(data.response);
                    }
                } catch (error) {
                    addMessage('Sorry, I had trouble connecting. Please try again.');
                }
                
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                userInput.focus();
            }
            
            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Initial greeting
            addMessage("Hello! I'm NeurodivergentHelper. How can I support you today?");
            userInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/query")
async def query(request: Request):
    """Query endpoint with session management"""
    data = await request.json()
    user_input = data.get("prompt", "").strip()
    
    if not user_input:
        return {"error": "No prompt provided."}
    
    session_id = get_session_id(request)
    
    try:
        # Add user message to session
        add_to_session(session_id, "user", user_input)
        
        # Load model (consider caching this)
        tokenizer, model, active_model = load_model()
        
        # Build context
        context = get_session_context(session_id)
        full_prompt = f"{DEFAULT_PROMPT}\n\n{context}\nNeurodivergentHelper:"
        
        # Generate response
        inputs = tokenizer(
            full_prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=2048  # Adjust based on your model
        ).to(model.device)
        
        outputs = model.generate(
            **inputs, 
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the new response part
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        
        # Add bot response to session
        add_to_session(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "model_used": active_model,
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"Error in query: {e}")
        return {"error": "Sorry, I encountered an issue processing your request."}

# --- Enhanced Gradio interface ---
def gradio_chat(user_input, history):
    """Enhanced Gradio chat with better error handling"""
    if not user_input.strip():
        return history, history
    
    try:
        tokenizer, model, active_model = load_model()
        
        # Build context from history
        context_parts = []
        for exchange in history[-3:]:  # Last 3 exchanges
            context_parts.append(f"User: {exchange[0]}")
            context_parts.append(f"NeurodivergentHelper: {exchange[1]}")
        
        context = "\n".join(context_parts)
        full_prompt = f"{DEFAULT_PROMPT}\n\n{context}\nUser: {user_input}\nNeurodivergentHelper:"
        
        inputs = tokenizer(
            full_prompt, 
            return_tensors="pt", 
            truncation=True,
            max_length=2048
        ).to(model.device)
        
        outputs = model.generate(
            **inputs, 
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the response
        if "NeurodivergentHelper:" in response_text:
            response_text = response_text.split("NeurodivergentHelper:")[-1].strip()
        
        history.append([user_input, response_text])
        return history, history
        
    except Exception as e:
        print(f"Gradio chat error: {e}")
        error_response = "I'm sorry, I encountered an issue. Please try again."
        history.append([user_input, error_response])
        return history, history

# --- Launch Gradio UI ---
if __name__ == "__main__":
    with gr.Blocks(
        title="NeurodivergentHelper",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 800px; margin: 0 auto; }
        .chat-message { margin-bottom: 10px; }
        """
    ) as demo:
        gr.Markdown("# NeurodivergentHelper")
        gr.Markdown("*A compassionate AI companion for neurodivergent individuals*")
        
        chatbot = gr.Chatbot(
            label="Chat",
            height=400,
            show_label=False,
            container=True
        )
        
        with gr.Row():
            user_input = gr.Textbox(
                label="Your message",
                placeholder="Type your message here...",
                container=False,
                scale=4
            )
            clear_btn = gr.Button("Clear", scale=1)
        
        # Event handlers
        user_input.submit(
            gradio_chat,
            inputs=[user_input, chatbot],
            outputs=[chatbot, chatbot],
            api_name="chat"
        )
        
        clear_btn.click(lambda: ([], []), outputs=[chatbot, chatbot])
    
    # Launch both FastAPI and Gradio
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
)
