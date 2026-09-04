import uuid
import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

_sessions = {}


def _cleanup_expired():
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now - s["_created"] > 3600]
    for sid in expired:
        del _sessions[sid]


def create_session() -> str:
    _cleanup_expired()
    sid = str(uuid.uuid4())
    _sessions[sid] = {"messages": [], "_created": time.time()}
    return sid


def get_history(session_id: str) -> list:
    _cleanup_expired()
    if session_id not in _sessions:
        return []
    return _sessions[session_id]["messages"]


def add_message(session_id: str, role: str, content: str):
    _cleanup_expired()
    if session_id not in _sessions:
        create_session()
    msg = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
    _sessions[session_id]["messages"].append(msg)


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]


def get_active_count() -> int:
    _cleanup_expired()
    return len(_sessions)