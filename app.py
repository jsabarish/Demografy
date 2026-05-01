"""
Demografy Insights Chatbot - Streamlit App
Run with: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import threading
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Demografy Insights",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&display=swap');

    html, body, .stApp, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: #f7f5fb;
        color: #272d2d;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 0.5rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }

    /* Left panel - expanded */
    .left-panel {
        background: #272d2d;
        border-radius: 10px;
        padding: 30px 24px;
        height: 92vh;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 18px 45px rgba(39,45,45,0.12);
    }
    .left-title {
        color: white;
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 12px;
        font-family: 'Open Sans', sans-serif;
    }
    .left-subtitle {
        color: rgba(255,255,255,0.72);
        font-size: 0.82rem;
        line-height: 1.5;
        margin-bottom: 22px;
    }
    .left-metric {
        border-top: 1px solid rgba(255,255,255,0.12);
        padding: 12px 0;
    }
    .left-metric-value {
        color: #d8f2d0;
        font-size: 1rem;
        font-weight: 800;
    }
    .left-metric-label {
        color: rgba(255,255,255,0.58);
        font-size: 0.75rem;
    }
    .left-examples {
        color: rgba(255,255,255,0.56);
        font-size: 0.72rem;
        margin-top: 26px;
        line-height: 1.8;
    }

    /* Left panel - collapsed */
    .left-collapsed {
        background: #272d2d;
        border-radius: 10px;
        padding: 24px 8px;
        height: 92vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }

    /* Login screen */
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        padding: 40px;
        background: white;
        border-radius: 12px;
        border: 1px solid #eee9fb;
        box-shadow: 0 18px 45px rgba(39,45,45,0.08);
        text-align: center;
    }
    .login-logo {
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 8px;
        font-family: 'Open Sans', sans-serif;
    }
    .login-subtitle {
        color: #888;
        font-size: 0.85rem;
        margin-bottom: 28px;
    }

    /* Tier badge */
    .tier-badge-pro {
        background: #d8f2d0;
        color: #333;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 6px;
    }
    .tier-badge-basic {
        background: #9a66ee;
        color: white;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 6px;
    }
    .tier-badge-free {
        background: #eee;
        color: #666;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 6px;
    }

    /* Question counter */
    .question-counter {
        background: rgba(94,23,235,0.07);
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 12px;
        font-size: 0.82rem;
        color: #5e17eb;
        font-weight: 600;
    }

    div[data-testid="column"] > div > div > div > button {
        background: transparent;
        border: none;
        color: #272d2d;
        font-size: 1.1rem;
        cursor: pointer;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialisation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "panel_open" not in st.session_state:
    st.session_state.panel_open = True
if "user" not in st.session_state:
    st.session_state.user = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "last_query_context" not in st.session_state:
    st.session_state.last_query_context = None

# Attempt to restore session from URL query param (used as a bridge from browser localStorage)
try:
    params = st.experimental_get_query_params()
    if "user" in params and st.session_state.user is None:
        try:
            from auth.rbac import get_user
            restored = get_user(params["user"][0])
            if restored is not None:
                st.session_state.user = restored
        except Exception:
            pass
except Exception:
    pass

# If browser localStorage has the user, inject JS to add it to the URL so server-side can pick it up
components.html("""
<script>
;(function(){
    try{
        const stored = localStorage.getItem('demografy_user');
        const urlParams = new URLSearchParams(window.location.search);
        if(stored && !urlParams.has('user')){
            try{
                const user = JSON.parse(stored);
                if(user && user.user_id){
                    urlParams.set('user', user.user_id);
                    // update URL without creating a new history entry
                    window.location.search = urlParams.toString();
                }
            }catch(e){}
        }
    }catch(e){}
})();
</script>
""", height=0)

# Login screen
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                D<span style="color:#5e17eb;">emografy</span>
            </div>
            <div class="login-subtitle">Insights Engine - enter your User ID to continue</div>
        </div>
        """, unsafe_allow_html=True)

        user_id_input = st.text_input(
            "User ID",
            placeholder="e.g. user_001",
            label_visibility="collapsed"
        )

        login_clicked = st.button("Sign In", use_container_width=True, type="primary")

        if login_clicked:
            if not user_id_input.strip():
                st.error("Please enter a User ID.")
            else:
                with st.spinner("Checking credentials..."):
                    try:
                        from auth.rbac import get_user
                        user = get_user(user_id_input.strip())

                        if user is None:
                            st.error("User not found or account is inactive. Please check your User ID.")
                        else:
                            st.session_state.user = user
                            st.session_state.question_count = 0
                            st.session_state.messages = []
                            st.session_state.last_query_context = None
                            # Log user data to server console for debugging
                            print("User logged in:", user)
                            # Persist minimal user info in browser localStorage and set URL param
                            try:
                                user_js = json.dumps({"user_id": user["user_id"], "tier": user.get("tier")})
                                components.html(
                                    f"<script>localStorage.setItem('demografy_user', JSON.stringify({user_js})); console.log('Demografy stored user:', {user_js});</script>",
                                    height=0,
                                )
                            except Exception:
                                pass
                            try:
                                st.experimental_set_query_params(user=user["user_id"])
                            except Exception:
                                pass
                            st.rerun()
                    except Exception as e:
                        st.error(f"Could not connect to user database. Error: {str(e)}")
    st.stop()

# Logged in - get user info
from auth.rbac import get_question_limit, is_limit_reached, should_show_warning

user = st.session_state.user
tier = user["tier"]
question_count = st.session_state.question_count
limit = get_question_limit(tier)

# Layout
if st.session_state.panel_open:
    left, right = st.columns([1, 3])
else:
    left, right = st.columns([0.08, 3])

# Left panel
with left:
    if st.session_state.panel_open:
        if st.button("Collapse", help="Collapse panel", key="collapse"):
            st.session_state.panel_open = False
            st.rerun()

        # Tier badge HTML
        tier_badge = f'<span class="tier-badge-{tier}">{tier.upper()}</span>'

        st.markdown(f"""
        <div class="left-panel">
            <div style="margin-bottom:20px;">
                <span style="color:white;font-size:1.4rem;font-weight:900;letter-spacing:-1px;font-family:'Open Sans',sans-serif;">
                    D<span style="color:#d8f2d0;">emografy</span>
                </span>
            </div>
            <div class="left-title">Insights<br>Engine</div>
            <div class="left-subtitle">
                Ask questions about Australian suburb demographics in plain English.
            </div>
            <div class="left-metric">
                <div class="left-metric-value">2,329</div>
                <div class="left-metric-label">SA2 areas</div>
            </div>
            <div class="left-metric">
                <div class="left-metric-value">10</div>
                <div class="left-metric-label">Demographic KPIs</div>
            </div>
            <div class="left-metric">
                <div class="left-metric-value">Live</div>
                <div class="left-metric-label">Live data answers</div>
            </div>

            <div style="margin-top: 24px; color: rgba(255,255,255,0.7); font-size: 0.78rem;">
                {user['user_id']} {tier_badge}<br>
                <div style="margin-top: 10px; background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px 14px;">
                    Questions: {question_count} / {limit}
                </div>
            </div>

            <div class="left-examples">
                Try asking:<br>
                "Top 3 diverse suburbs in Victoria?"<br>
                "Avg prosperity score in NSW?"<br>
                "Cheapest rentals in QLD?"
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Logout button
        if st.button("Sign Out", key="logout"):
            st.session_state.user = None
            st.session_state.question_count = 0
            st.session_state.messages = []
            st.session_state.last_query_context = None
            # Clear persisted browser session and remove query param
            try:
                components.html(
                    "<script>localStorage.removeItem('demografy_user'); if(window.history && history.replaceState){ const u=new URL(window.location); u.searchParams.delete('user'); history.replaceState(null,'', u); }</script>",
                    height=0,
                )
            except Exception:
                pass
            try:
                st.experimental_set_query_params()
            except Exception:
                pass
            st.rerun()

    else:
        if st.button("Expand", help="Expand panel", key="expand"):
            st.session_state.panel_open = True
            st.rerun()

        st.markdown("""
        <div class="left-collapsed">
            <div style="color:white;font-weight:900;font-size:1rem;writing-mode:vertical-rl;
                        text-orientation:mixed;letter-spacing:2px;margin-top:12px;font-family:'Open Sans',sans-serif;">
                DEMOGRAFY
            </div>
        </div>
        """, unsafe_allow_html=True)

# Right panel
with right:
    st.markdown("### Demografy Insights Chat")
    st.caption("Ask questions about Australian suburb demographics in plain English.")
    st.divider()

    if not st.session_state.messages:
        st.markdown("""
        I can help you explore Australian suburb-level demographic insights, including population,
        prosperity, diversity, migration, education, housing, rental affordability, stability,
        and family composition.

        You can ask things like:

        - What are the top 5 most diverse suburbs in New South Wales?
        - What is the average learning level in Victoria?
        - Show me suburbs with high resident anchor and high resident equity.
        - Compare average home ownership versus rental access by state.
        """)

    # Chat history
    for msg in st.session_state.messages:
        if msg["role"] == "assistant.progress":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sql"):
                st.markdown("_Query details hidden for privacy._")

    # Tier limit checks
    if is_limit_reached(tier, question_count):
        # Disable input, show upgrade prompt
        st.error(
            f"You've reached your **{tier.upper()}** plan limit of **{limit} questions** this session.\n\n"
            f"Upgrade your plan to continue asking questions."
        )
        st.chat_input("Question limit reached - upgrade to continue", disabled=True)

    else:
        # Show warning if approaching limit
        if should_show_warning(tier, question_count):
            remaining = limit - question_count
            st.warning(f"You have **{remaining} question{'s' if remaining != 1 else ''}** remaining on your {tier.upper()} plan this session.")

        # Chat input
        question = st.chat_input("e.g. What are the top 3 suburbs in Victoria by diversity index?")

        if question:
            st.session_state.question_count += 1
            st.session_state.messages.append({"role": "user", "content": question})

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                sql_query = None
                try:
                    from agent.sql_agent import ask
                    from agent.conversation import (
                        answer_contextual_question,
                        polish_answer,
                        resolve_followup,
                        sanitize_user_answer,
                    )

                    contextual_answer = answer_contextual_question(
                        question,
                        st.session_state.last_query_context,
                    )
                    if contextual_answer:
                        answer = sanitize_user_answer(contextual_answer)
                        sql_query = None
                        st.markdown(answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sql": sql_query,
                        })
                        st.rerun()

                    resolved_question, rewrite_note = resolve_followup(
                        question,
                        st.session_state.last_query_context,
                    )

                    # Run the agent call in a background thread and show a progress bar.
                    progress_expander = st.expander("Query progress", expanded=True)
                    progress_bar = progress_expander.progress(0)
                    progress_text = progress_expander.empty()

                    result = {"answer": None, "sql": None, "error": None}

                    def run_agent():
                        try:
                            a, s = ask(resolved_question)
                            result["answer"] = a
                            result["sql"] = s
                        except Exception as e:
                            result["error"] = e

                    t = threading.Thread(target=run_agent)
                    t.start()

                    # Phase-based progress messages (keeps UI in main thread)
                    phases = [
                        ("Preparing request", 0),
                        ("Checking access", 8),
                        ("Selecting the right metric", 18),
                        ("Building query", 30),
                        ("Running query", 50),
                        ("Reading results", 75),
                        ("Validating response", 88),
                        ("Formatting answer", 95),
                    ]

                    logs = []
                    start_time = time.time()
                    current_phase = -1

                    # Poll the thread and update phase messages until finished
                    while t.is_alive():
                        # advance phase if needed
                        next_phase = min(current_phase + 1, len(phases)-1)
                        # Pick phase based on elapsed proportion - simple paced advancement.
                        elapsed = time.time() - start_time
                        # map elapsed to an index by pacing (short heuristic)
                        if elapsed < 0.6:
                            idx = 0
                        elif elapsed < 1.2:
                            idx = 1
                        elif elapsed < 1.9:
                            idx = 2
                        elif elapsed < 2.6:
                            idx = 3
                        elif elapsed < 4.0:
                            idx = 4
                        elif elapsed < 5.5:
                            idx = 5
                        elif elapsed < 6.0:
                            idx = 6
                        else:
                            idx = min(len(phases)-1, current_phase+1)

                        if idx > current_phase:
                            current_phase = idx
                            msg, pct = phases[current_phase]
                            logs.append(msg)
                            # render logs inside expander
                            progress_text.markdown("\n".join([f"- {l}" for l in logs]))
                            progress_bar.progress(pct)

                        time.sleep(0.25)

                    t.join()
                    # Agent finished - append final logs and elapsed.
                    if result["error"]:
                        raise result["error"]

                    elapsed_total = time.time() - start_time
                    logs.append(f"Done - results ready ({elapsed_total:.1f}s)")
                    progress_text.markdown("\n".join([f"- {l}" for l in logs]))
                    progress_bar.progress(100)

                    answer = result["answer"]
                    sql_query = result["sql"]
                    answer = polish_answer(resolved_question, answer, sql_query, rewrite_note)
                    st.session_state.last_query_context = {
                        "raw_question": question,
                        "question": resolved_question,
                        "answer": answer,
                        "sql": sql_query,
                    }

                except Exception:
                    try:
                        import os
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        from langchain_core.messages import SystemMessage, HumanMessage
                        with st.spinner("Thinking..."):
                            llm = ChatGoogleGenerativeAI(
                                model="gemini-2.5-flash",
                                google_api_key=os.getenv("GEMINI_API_KEY"),
                                temperature=0,
                            )
                            response = llm.invoke([
                                SystemMessage(content=(
                                    "You are Demografy, an AI assistant specialising in Australian suburb demographics. "
                                    "You have knowledge of ABS census data, suburb statistics, KPIs like diversity index, "
                                    "prosperity score, rental costs, population density, and more. "
                                    "Answer questions helpfully and concisely. "
                                    "Never mention internal table names, column names, SQL, schemas, or implementation details. "
                                    "Note: live data is not yet connected, so answers are based on general knowledge."
                                )),
                                HumanMessage(content=question),
                            ])
                        answer = response.content + "\n\n> *Live data not connected yet - this answer is from general AI knowledge, not the Demografy database.*"
                        answer = sanitize_user_answer(answer)
                    except Exception as e2:
                        answer = f"Could not get a response.\n\n**Error:** {str(e2)}"

                st.markdown(answer)
                if sql_query:
                    st.markdown("_Query details hidden for privacy._")

            st.session_state.messages.append({"role": "assistant", "content": answer, "sql": sql_query})
            st.rerun()
