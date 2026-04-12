"""
Demografy Insights Chatbot — Streamlit App
Run with: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Demografy Insights",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Left panel — expanded */
    .left-panel {
        background-color: #7C3AED;
        border-radius: 16px;
        padding: 32px 24px;
        height: 92vh;
    }
    .left-title {
        color: white;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    .left-subtitle {
        color: rgba(255,255,255,0.75);
        font-size: 0.82rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    .left-tag {
        background: rgba(255,255,255,0.15);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        display: inline-block;
        margin-bottom: 6px;
    }
    .left-examples {
        color: rgba(255,255,255,0.5);
        font-size: 0.72rem;
        margin-top: 24px;
        line-height: 1.8;
    }

    /* Left panel — collapsed (just icon strip) */
    .left-collapsed {
        background-color: #7C3AED;
        border-radius: 16px;
        padding: 24px 8px;
        height: 92vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }

    /* Toggle button */
    div[data-testid="column"] > div > div > div > button {
        background: transparent;
        border: none;
        color: white;
        font-size: 1.1rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "panel_open" not in st.session_state:
    st.session_state.panel_open = True

# ── Layout ────────────────────────────────────────────────────────────────────
# Column ratio changes based on whether the left panel is open or collapsed
if st.session_state.panel_open:
    left, right = st.columns([1, 3])
else:
    left, right = st.columns([0.08, 3])

# ── LEFT PANEL ────────────────────────────────────────────────────────────────
with left:
    if st.session_state.panel_open:
        # Toggle button to collapse
        if st.button("◀", help="Collapse panel", key="collapse"):
            st.session_state.panel_open = False
            st.rerun()

        st.markdown("""
        <div class="left-panel">
            <div style="margin-bottom:20px;">
                <span style="color:white;font-size:1.4rem;font-weight:900;letter-spacing:-1px;">
                    D<span style="color:#C4B5FD;">emografy</span>
                </span>
            </div>
            <div class="left-title">Insights<br>Engine</div>
            <div class="left-subtitle">
                Ask questions about Australian suburb demographics in plain English.
            </div>
            <div class="left-tag">🏘️ 2,329 suburbs</div><br>
            <div class="left-tag">📊 10 KPIs</div><br>
            <div class="left-tag">🤖 Gemini AI</div>
            <div class="left-examples">
                Try asking:<br>
                "Top 3 diverse suburbs in Victoria?"<br>
                "Avg prosperity score in NSW?"<br>
                "Cheapest rentals in QLD?"
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Toggle button to expand
        if st.button("▶", help="Expand panel", key="expand"):
            st.session_state.panel_open = True
            st.rerun()

        st.markdown("""
        <div class="left-collapsed">
            <div style="color:white;font-weight:900;font-size:1rem;writing-mode:vertical-rl;
                        text-orientation:mixed;letter-spacing:2px;margin-top:12px;">
                DEMOGRAFY
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT PANEL ───────────────────────────────────────────────────────────────
with right:
    st.markdown("### 💬 Demografy Insights Chat")
    st.caption("Ask questions about Australian suburb demographics in plain English.")
    st.divider()

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    question = st.chat_input("e.g. What are the top 3 suburbs in Victoria by diversity index?")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analysing suburb data..."):
                try:
                    from agent.sql_agent import ask
                    answer = ask(question)
                except Exception as e:
                    answer = (
                        f"⚠️ BigQuery not connected yet.\n\n"
                        f"**Reason:** {str(e)}\n\n"
                        "Once the service account key is added, this will work fully."
                    )
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
