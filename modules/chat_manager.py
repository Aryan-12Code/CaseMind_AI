"""
chat_manager.py — Chat interaction logic for CaseMind AI.

Manages the chat loop: sends user questions with evidence context
to Gemini, parses structured responses, and provides rendering helpers.
"""

import re
import streamlit as st
from modules.ai_engine import query_evidence
from modules.citation_engine import build_evidence_context
from modules.conversation_history import save_chat


def ask_question(api_key: str, question: str) -> dict:
    """
    Send a user question to the AI with evidence context.

    Args:
        api_key: Gemini API key.
        question: The user's question text.

    Returns:
        Dict with keys: answer, source, evidence, confidence, raw.
    """
    context = build_evidence_context()

    if not context:
        return {
            "answer": "No processed evidence found. Please upload and process files first.",
            "source": "N/A",
            "evidence": "N/A",
            "raw": "",
        }

    raw_response = query_evidence(api_key, question, context)

    # Parse structured response
    parsed = _parse_ai_response(raw_response)

    # Save to conversation history
    save_chat(
        question=question,
        answer=parsed["answer"],
        sources=parsed["source"],
    )

    return parsed


def _parse_ai_response(raw: str) -> dict:
    """
    Parse the structured AI response into components.

    Expected format:
        **Answer:** ...
        **Source:** ...
        **Supporting Evidence:** ...
        **Confidence:** X%
    """
    result = {
        "answer": raw,
        "source": "",
        "evidence": "",
        "raw": raw,
    }

    # Try to extract structured fields
    answer_match = re.search(r"\*\*Answer:\*\*\s*(.*?)(?=\*\*Source:|\*\*Supporting|\Z)", raw, re.DOTALL)
    source_match = re.search(r"\*\*Source:\*\*\s*(.*?)(?=\*\*Supporting|\Z)", raw, re.DOTALL)
    evidence_match = re.search(r"\*\*Supporting Evidence:\*\*\s*(.*?)(?=\Z)", raw, re.DOTALL)

    if answer_match:
        result["answer"] = answer_match.group(1).strip()
    if source_match:
        result["source"] = source_match.group(1).strip()
    if evidence_match:
        result["evidence"] = evidence_match.group(1).strip()

    return result


def render_ai_message(response: dict) -> None:
    """Render an AI response as a styled message with citations."""

    # Main answer
    st.markdown(f"""
    <div style="background-color:#262730; padding:15px; border-radius:12px;
                margin-bottom:8px; border-left:4px solid #0068c9;">
        <p style="color:#eee; line-height:1.6; margin:0;">{response['answer']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Citation details in columns
    if response.get("source") or response.get("evidence"):
        col1, col2 = st.columns([1, 2])

        with col1:
            if response.get("source"):
                st.markdown(f"""
                <div style="background-color:#1a1a2e; padding:10px; border-radius:8px; height: 100%;">
                    <small style="color:#888;">📄 Source</small><br/>
                    <span style="color:#0068c9;">{response['source']}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            if response.get("evidence"):
                evidence_short = response["evidence"][:250]
                if len(response["evidence"]) > 250:
                    evidence_short += "..."
                st.markdown(f"""
                <div style="background-color:#1a1a2e; padding:10px; border-radius:8px; height: 100%;">
                    <small style="color:#888;">📝 Supporting Evidence</small><br/>
                    <span style="color:#aaa; font-size:0.85em;">"{evidence_short}"</span>
                </div>
                """, unsafe_allow_html=True)
