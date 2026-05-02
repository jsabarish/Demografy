"""Per-user cooldown timestamps that survive a hard refresh.

When a user hits their tier's question limit we stash a wall-clock
``cooldown_until`` (epoch seconds) so the chat widget can show a live
countdown and refuse to submit further questions until it elapses. Once
the timer is up the engine resets ``question_count`` to zero, giving the
user a fresh "mini-session" without changing tier limits.

Storage
-------
A single JSON file ``ChatHistory/_cooldowns.json`` mapping ``user_id`` to
its current ``cooldown_until``. We deliberately reuse the existing chat
history directory so:

* there is one place to look on disk,
* the same ``*.json`` ``.gitignore`` rule keeps it out of version control,
* deployments that already mount ``ChatHistory/`` get persistence for
  free.

All I/O is best-effort (``OSError`` swallowed) so a broken disk never
blocks chat. Callers must be tolerant of ``None`` values regardless.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


HISTORY_DIR = Path(__file__).resolve().parent.parent / "ChatHistory"
_STORE_PATH = HISTORY_DIR / "_cooldowns.json"


def _load_all() -> Dict[str, float]:
    if not _STORE_PATH.exists():
        return {}
    try:
        raw = _STORE_PATH.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, float] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            continue
        try:
            out[key] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def _save_all(data: Dict[str, float]) -> None:
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        _STORE_PATH.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        # Disk is best-effort; a missed persist just means the cooldown
        # won't survive a refresh but in-memory state still blocks the UI.
        pass


def get_cooldown_until(user_id: str) -> Optional[float]:
    """Return the active cooldown end (epoch seconds) for ``user_id`` or ``None``."""
    if not user_id:
        return None
    return _load_all().get(user_id)


def set_cooldown_until(user_id: str, ts: float) -> None:
    """Persist ``ts`` (epoch seconds) as the active cooldown end for ``user_id``."""
    if not user_id:
        return
    data = _load_all()
    try:
        data[user_id] = float(ts)
    except (TypeError, ValueError):
        return
    _save_all(data)


def clear_cooldown(user_id: str) -> None:
    """Remove any persisted cooldown for ``user_id`` (no-op if absent)."""
    if not user_id:
        return
    data = _load_all()
    if user_id in data:
        data.pop(user_id, None)
        _save_all(data)
