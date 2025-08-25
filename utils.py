import json
import os

sessions = {}

def get_session_id(user_agent: str, client_ip: str) -> str:
    return f"{client_ip}_{hash(user_agent)}"

def add_to_session(session_id: str, role: str, content: str, max_history: int = 10):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})
    if len(sessions[session_id]) > max_history:
        sessions[session_id] = sessions[session_id][-max_history:]

def get_session_context(session_id: str, last_n: int = 5) -> str:
    if session_id not in sessions:
        return ""
    context_parts = []
    for msg in sessions[session_id][-last_n:]:
        prefix = "User: " if msg["role"] == "user" else "NeurodivergentHelper: "
        context_parts.append(f"{prefix}{msg['content']}")
    return "\n".join(context_parts)

def export_session(session_id: str, format="txt"):
    if session_id not in sessions:
        return None
    if format == "txt":
        return "\n".join([f"{m['role']}: {m['content']}" for m in sessions[session_id]])
    elif format == "json":
        return json.dumps(sessions[session_id], indent=2)
