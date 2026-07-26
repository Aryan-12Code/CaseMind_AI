"""
chat_view.py — AI Chat page for CaseMind AI.

Live Gemini-powered chatbot that answers questions using only
uploaded evidence. Includes conversation history, suggested
questions, and citation rendering.
"""

import time
import html as _html
import streamlit as st
from modules.database import init_db
from modules.chat_manager import ask_question, render_ai_message
from modules.conversation_history import render_history_panel
from modules.citation_engine import build_evidence_context


# ── Default suggested questions ──────────────────────────────────────────────
DEFAULT_SUGGESTIONS = [
    "Summarize the case",
    "Who is mentioned most?",
    "Show money transactions",
    "List suspicious keywords",
    "List all important dates",
    "Which files mention passwords?",
]


def render() -> None:
    """Render the AI Chat page."""
    init_db()

    st.title("💬 AI Chat")
    st.write("Ask questions about your uploaded evidence. The AI answers **only** from your files.")
    st.markdown("---")

    # ── Check API key ────────────────────────────────────────────────────────
    api_key = st.session_state.get("groq_api_key", "")
    if not api_key:
        st.warning("⚠️ Please set your Groq API key in **Settings** first.")
        return

    # ── Check evidence ───────────────────────────────────────────────────────
    context = build_evidence_context()
    if not context:
        st.info("📂 No processed evidence found. Upload files in **Upload Evidence** first.")
        return

    # ── Layout: Chat + History sidebar ───────────────────────────────────────
    chat_col, history_col = st.columns([3, 1])

    with history_col:
        st.markdown("### 📜 History")
        reopened = render_history_panel()
        if reopened:
            st.session_state["chat_prefill"] = reopened
            st.rerun()

    with chat_col:
        # ── Initialize chat messages in session state ────────────────────────
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {
                    "role": "ai",
                    "content": {
                        "answer": "Hello! I am CaseMind AI. Ask me anything about your uploaded evidence.",
                        "source": "", "evidence": "", "confidence": "", "raw": "",
                    }
                }
            ]

        # ── Render chat history ──────────────────────────────────────────────
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                safe_content = _html.escape(msg['content'])
                st.markdown(f"""
                <div style="background-color:#0068c9; color:white; padding:12px 16px;
                            border-radius:15px 15px 0 15px; margin-bottom:12px;
                            max-width:75%; margin-left:auto; text-align:right;">
                    {safe_content}
                </div>
                """, unsafe_allow_html=True)
            else:
                render_ai_message(msg["content"])

        st.markdown("---")

        # ── Suggested questions ──────────────────────────────────────────────
        def populate_input(q_text):
            st.session_state["chat_input_field"] = q_text

        suggestions = st.session_state.get("ai_suggestions", DEFAULT_SUGGESTIONS)
        st.caption("💡 Suggested questions:")
        suggestion_cols = st.columns(min(len(suggestions), 3))
        for i, q in enumerate(suggestions[:6]):
            with suggestion_cols[i % 3]:
                st.button(q, key=f"sug_{i}", use_container_width=True, on_click=populate_input, args=(q,))

        # ── Input area ───────────────────────────────────────────────────────
        def on_chat_submit():
            q = st.session_state.get("chat_input_field", "").strip()
            if q:
                st.session_state["pending_q"] = q
                st.session_state["chat_input_field"] = ""

        col_input, col_btn = st.columns([6, 1])
        with col_input:
            user_input = st.text_input(
                "Ask a question...",
                key="chat_input_field",
                on_change=on_chat_submit,
                label_visibility="collapsed",
                placeholder="Type your question about the evidence...",
            )
        with col_btn:
            st.button("Ask", use_container_width=True, type="primary", on_click=on_chat_submit)

        # ── Process question ─────────────────────────────────────────────────
        if st.session_state.get("pending_q"):
            q = st.session_state.pop("pending_q")
            _handle_question(api_key, q)


def _handle_question(api_key: str, question: str) -> None:
    """Send a question to the AI and update the chat."""
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": question,
    })

    # Show loading animation
    with st.status("Analyzing uploaded evidence...", expanded=True) as status:
        time.sleep(0.4)
        status.update(label="Searching documents...")
        time.sleep(0.4)
        status.update(label="Cross-checking entities...")
        time.sleep(0.4)
        status.update(label="Generating answer...")
        
        response = ask_question(api_key, question)
        
        status.update(label="Response generated!", state="complete", expanded=False)

    # Add AI response
    st.session_state.chat_messages.append({
        "role": "ai",
        "content": response,
    })

    st.rerun()
