"""Chat lifecycle: take a user question -> run the agent -> append the reply.

Owns all session-state mutations for ``chat_messages``. Designed to run
inside an ``@st.fragment`` so the (potentially slow) ``ask()`` call only
shows a fragment-scoped running indicator, not the page-wide fade overlay.

Two functions form the state machine driven by ``app_v4.py``:

  * ``maybe_consume_bridge`` - turns a fresh ``{question, ts}`` payload from
    the chat widget into chat-history + pending-flag mutations. Deduped by
    timestamp so reruns that surface the same sticky payload don't
    double-process.

  * ``resolve_pending_question`` - if a pending question is stashed, calls
    ``agent.sql_agent.ask`` synchronously and appends the assistant reply.
    The chat widget JS shows the optimistic Thinking bubble, so we don't
    need any extra rerun/arming step on the Python side.
"""

from typing import Optional

import streamlit as st

from auth.rbac import (
    get_question_limit,
    is_limit_reached,
    should_show_warning,
)


def _get_tier() -> str:
    user = st.session_state.get("user") or {}
    return user.get("tier", "free")


def _append(role: str, content: str) -> None:
    st.session_state.chat_messages.append({"role": role, "content": content})


def handle_new_question(question: str) -> None:
    """Append the user message and stash the question for ``resolve``."""
    question = (question or "").strip()
    if not question:
        return

    tier = _get_tier()
    question_count = int(st.session_state.get("question_count", 0))

    _append("user", question)

    if is_limit_reached(tier, question_count):
        _append(
            "assistant",
            "You\u2019ve reached your question limit for this session. "
            "Upgrade your tier to continue asking questions.",
        )
        return

    st.session_state.chat_pending = True
    st.session_state.chat_pending_question = question


def resolve_pending_question() -> None:
    """If a question is stashed, invoke the agent and append the reply."""
    if not st.session_state.get("chat_pending"):
        return

    question = st.session_state.get("chat_pending_question")
    if not question:
        st.session_state.chat_pending = False
        return

    # Defer the import so we only pay LangChain / google-genai / BigQuery
    # startup cost once a real question is in flight.
    from agent.sql_agent import ask

    try:
        answer, _sql = ask(question)
    except Exception as exc:
        answer = f"Sorry, I hit an error answering that. ({exc})"

    _append(
        "assistant",
        answer or "Sorry, I could not format an answer for that query.",
    )

    tier = _get_tier()
    question_count = int(st.session_state.get("question_count", 0)) + 1
    st.session_state.question_count = question_count

    if should_show_warning(tier, question_count):
        remaining = max(get_question_limit(tier) - question_count, 0)
        plural = "s" if remaining != 1 else ""
        _append(
            "assistant",
            f"Heads up: only {remaining} question{plural} left in this session.",
        )

    st.session_state.chat_pending = False
    st.session_state.chat_pending_question = None


def maybe_consume_bridge(bridge_value: Optional[dict]) -> None:
    """Forward a fresh chat-widget payload into ``handle_new_question``.

    The chat widget's component value is sticky across reruns, so we dedupe
    by ``ts`` using ``st.session_state.chat_last_ts``. A None payload (no
    submission yet) is a no-op.
    """
    if not bridge_value:
        return

    ts = bridge_value.get("ts")
    question = bridge_value.get("question")
    if not question or ts is None:
        return

    last_ts = st.session_state.get("chat_last_ts")
    if last_ts == ts:
        return

    st.session_state.chat_last_ts = ts
    handle_new_question(question)
