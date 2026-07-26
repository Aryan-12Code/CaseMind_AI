"""
conversation_history.py — Conversation persistence for CaseMind AI.

Stores every question/answer pair in SQLite and provides
a UI component to browse and reopen past conversations.
"""

import streamlit as st
from datetime import datetime
from modules.database import (
    init_db,
    add_conversation,
    get_all_conversations,
    clear_conversations,
)


def save_chat(question: str, answer: str, sources: str = "", confidence: str = "") -> None:
    """
    Save a question-answer pair to the database.

    Args:
        question: The user's question.
        answer: The AI's response.
        sources: Source file(s) referenced.
        confidence: Confidence level string.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    add_conversation(
        question=question,
        answer=answer,
        sources=sources,
        confidence=confidence,
        timestamp=timestamp,
    )


def render_history_panel() -> str | None:
    """
    Render the conversation history as a browsable panel.

    Returns:
        The question text if the user clicks "Reopen" on a past conversation,
        else None.
    """
    conversations = get_all_conversations()

    if not conversations:
        st.caption("No conversation history yet.")
        return None

    reopened_question = None

    for conv in conversations[:20]:  # Show last 20
        with st.expander(
            f"🕒 {conv['timestamp']} — {conv['question'][:60]}{'...' if len(conv['question']) > 60 else ''}",
            expanded=False,
        ):
            st.markdown(f"**Q:** {conv['question']}")
            st.markdown(f"**A:** {conv['answer'][:500]}{'...' if len(conv['answer']) > 500 else ''}")
            if conv.get("sources"):
                st.caption(f"📄 Sources: {conv['sources']}")
            if conv.get("confidence"):
                st.caption(f"🎯 Confidence: {conv['confidence']}")

            if st.button("🔄 Ask Again", key=f"reopen_{conv['id']}"):
                reopened_question = conv["question"]

    # Clear history button
    st.markdown("---")
    if st.button("🗑️ Clear All History", type="secondary"):
        clear_conversations()
        st.success("Conversation history cleared.")
        st.rerun()

    return reopened_question
