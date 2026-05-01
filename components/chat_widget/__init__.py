"""Demografy chat widget custom component.

A single, persistent iframe that owns:
  - the chat FAB (toggles the panel open/closed)
  - the chat panel header, message thread, and input
  - the expand/split layout toggle

Communication contract:
  - Python -> JS: ``messages``, ``pending``, ``limit_reached`` are pushed to
    the iframe as component args on every Streamlit render. JS reconciles the
    DOM in place (no innerHTML rewrite, no iframe reload).
  - JS -> Python: when the user submits, the iframe immediately renders the
    user bubble + a "Thinking..." bubble locally (optimistic UI), then calls
    ``Streamlit.setComponentValue({question, ts})`` so Python can run the
    agent and append the assistant reply.

This is declared as a custom component (not ``components.html``) so Streamlit
reuses the same iframe across reruns instead of reloading it. That kills the
visible flicker the previous body-embedded chat had.
"""

from pathlib import Path
from typing import Iterable, Optional

import streamlit.components.v1 as components


CHAT_WIDGET_KEY = "demografy_chat_widget_v1"

_FRONTEND_DIR = Path(__file__).parent / "frontend"

_component_func = components.declare_component(
    "demografy_chat_widget",
    path=str(_FRONTEND_DIR),
)


def render_chat_widget(
    messages: Iterable[dict],
    pending: bool,
    limit_reached: bool,
    *,
    key: str = CHAT_WIDGET_KEY,
) -> Optional[dict]:
    """Render the persistent chat widget.

    Returns the latest ``{"question": str, "ts": int}`` payload submitted by
    the user, or ``None`` if no submission has happened yet. The same payload
    is sticky across reruns; callers must dedupe by ``ts``.
    """
    return _component_func(
        messages=list(messages or []),
        pending=bool(pending),
        limit_reached=bool(limit_reached),
        default=None,
        key=key,
    )
