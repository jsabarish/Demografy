"""Invisible bridge component: receives postMessage from the body iframe
and surfaces user questions to Python via Streamlit's component value channel.

Designed to be a one-way pipe (iframe -> Python). The body iframe owns chat
visuals; Python owns chat state. Decoupling them through this bridge keeps
the existing UI fully isolated and avoids circular re-render loops.
"""

from pathlib import Path
from typing import Optional

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "frontend"

_component_func = components.declare_component(
    "demografy_chat_bridge",
    path=str(_FRONTEND_DIR),
)


def render_bridge(key: str = "demografy_chat_bridge") -> Optional[dict]:
    """Render the invisible bridge iframe and return the latest payload.

    Returns a dict like ``{"question": "...", "ts": 1700000000000}`` when a new
    message arrives from the body iframe, otherwise ``None``.
    """
    return _component_func(default=None, key=key, height=0, width=0)
