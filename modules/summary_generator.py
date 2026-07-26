"""
summary_generator.py — Case summary generation for CaseMind AI.

Orchestrates calling the AI engine to produce a comprehensive
investigation summary from all processed evidence.
"""

import streamlit as st
from modules.ai_engine import generate_case_summary
from modules.citation_engine import build_evidence_context


def generate_full_summary(api_key: str) -> dict | None:
    """
    Generate a full case summary using all processed evidence.

    Args:
        api_key: Google Gemini API key.

    Returns:
        Dictionary with summary sections, or None on failure.
    """
    context = build_evidence_context()

    if not context:
        st.warning("⚠️ No processed evidence found. Upload and process files first.")
        return None

    return generate_case_summary(api_key, context)


def render_summary_cards(summary: dict) -> None:
    """Render the case summary as styled cards in the Streamlit UI."""

    # ── Overall Case Summary ─────────────────────────────────────────────────
    case_summary = summary.get("case_summary", "No summary available.")
    st.markdown(f"""
    <div style="background-color:#262730; padding:20px; border-radius:12px;
                border-left:5px solid #0068c9; margin-bottom:15px;">
        <h3 style="margin:0 0 10px 0;">📋 Case Summary</h3>
        <p style="color:#ccc; line-height:1.6;">{case_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Grid sections ────────────────────────────────────────────────────────
    _sections = [
        ("🔍 Important Findings", "important_findings", "#FF9800"),
        ("👤 People Mentioned", "people_mentioned", "#2196F3"),
        ("🏢 Organizations", "organizations", "#9C27B0"),
        ("📍 Locations", "locations", "#4CAF50"),
        ("📅 Important Dates", "important_dates", "#E91E63"),
        ("💰 Monetary Transactions", "monetary_transactions", "#FF5722"),
        ("⚠️ Suspicious Keywords", "suspicious_keywords", "#F44336"),
        ("💡 Observations", "observations", "#00BCD4"),
    ]

    cols = st.columns(2)
    for idx, (title, key, color) in enumerate(_sections):
        items = summary.get(key, [])
        if not items:
            continue

        with cols[idx % 2]:
            items_html = "".join(
                f"<li style='color:#ccc; margin-bottom:4px;'>{item}</li>"
                for item in items
            )
            st.markdown(f"""
            <div style="background-color:#262730; padding:15px; border-radius:10px;
                        border-left:4px solid {color}; margin-bottom:12px;">
                <h4 style="margin:0 0 8px 0;">{title} ({len(items)})</h4>
                <ul style="margin:0; padding-left:20px;">{items_html}</ul>
            </div>
            """, unsafe_allow_html=True)


def render_suggested_questions(summary: dict) -> str | None:
    """
    Render suggested follow-up questions as clickable chips.

    Returns:
        The question text if a user clicks one, else None.
    """
    questions = summary.get("suggested_questions", [])
    if not questions:
        return None

    st.subheader("💡 Suggested Questions")
    clicked = None
    cols = st.columns(min(len(questions), 3))
    for i, q in enumerate(questions):
        with cols[i % 3]:
            if st.button(f"❓ {q}", key=f"suggested_q_{i}", use_container_width=True):
                clicked = q
    return clicked
