"""
Chat history storage for Demografy Insights Chatbot.
Stores chat sessions as JSON files per user in the chat_history/ directory.

Each file: chat_history/{user_id}.json
Structure:
{
  "user_id": "user_001",
  "sessions": [
    {
      "session_id": "uuid",
      "title": "First 60 chars of first question",
      "date": "2026-04-22",
      "created_at": "2026-04-22T10:30:00",
      "messages": [
        {"role": "user", "content": "...", "sql": null},
        {"role": "assistant", "content": "...", "sql": "SELECT ..."}
      ]
    }
  ]
}
"""

import json
import os
from datetime import datetime

HISTORY_DIR = "chat_history"
MAX_SESSIONS = 50  # Max sessions stored per user


def _get_path(user_id: str) -> str:
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return os.path.join(HISTORY_DIR, f"{user_id}.json")


def load_history(user_id: str) -> list:
    """Load all chat sessions for a user. Returns list of sessions, newest first."""
    path = _get_path(user_id)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("sessions", [])
    except (json.JSONDecodeError, KeyError):
        return []


def save_session(user_id: str, session_id: str, title: str, messages: list) -> None:
    """Save or update a chat session. Inserts new sessions at the front."""
    if not messages:
        return

    path = _get_path(user_id)
    sessions = load_history(user_id)

    for session in sessions:
        if session["session_id"] == session_id:
            session["messages"] = messages
            session["title"] = title
            _write(path, user_id, sessions)
            return

    sessions.insert(0, {
        "session_id": session_id,
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(),
        "messages": messages,
    })

    _write(path, user_id, sessions[:MAX_SESSIONS])


def _write(path: str, user_id: str, sessions: list) -> None:
    with open(path, "w") as f:
        json.dump({"user_id": user_id, "sessions": sessions}, f, indent=2)
