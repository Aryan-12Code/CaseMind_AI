"""
insight_generator.py — Automatic AI insights for CaseMind AI.

Generates investigation insights such as most mentioned person,
most important date/location/keyword, and suspicious activity.
"""

import streamlit as st
from modules.ai_engine import generate_insights as _ai_generate_insights
from modules.citation_engine import build_evidence_context


def generate_and_render_insights(api_key: str) -> None:
    """
    Generate AI insights and render them as styled cards.

    Args:
        api_key: Google Gemini API key.
    """
    context = build_evidence_context()
    if not context:
        st.info("No evidence available for insight generation.")
        return

    insights = _ai_generate_insights(api_key, context)
    if not insights:
        st.warning("Could not generate insights. Please try again.")
        return

    st.subheader("🧠 AI Insights")

    # ── Render insight cards in a grid ────────────────────────────────────────
    _cards = [
        {
            "icon": "👤",
            "title": "Most Mentioned Person",
            "data": insights.get("most_mentioned_person", {}),
            "color": "#2196F3",
            "fields": ["name", "count_approx", "context"],
        },
        {
            "icon": "📅",
            "title": "Most Important Date",
            "data": insights.get("most_important_date", {}),
            "color": "#E91E63",
            "fields": ["date", "context"],
        },
        {
            "icon": "📍",
            "title": "Most Important Location",
            "data": insights.get("most_important_location", {}),
            "color": "#4CAF50",
            "fields": ["location", "context"],
        },
        {
            "icon": "🔑",
            "title": "Most Frequent Keyword",
            "data": insights.get("most_frequent_keyword", {}),
            "color": "#FF9800",
            "fields": ["keyword", "context"],
        },
        {
            "icon": "⚠️",
            "title": "Possible Suspicious Activity",
            "data": insights.get("suspicious_activity", {}),
            "color": "#F44336",
            "fields": ["description", "severity"],
        },
    ]

    cols = st.columns(3)
    for i, card in enumerate(_cards):
        data = card["data"]
        if not data or not isinstance(data, dict):
            continue

        # Build the content lines
        content_lines = []
        for field in card["fields"]:
            val = data.get(field)
            if val and str(val) != "Not found" and val != 0:
                label = field.replace("_", " ").title()
                content_lines.append(f"<strong>{label}:</strong> {val}")

        if not content_lines:
            continue

        content_html = "<br/>".join(content_lines)

        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color:#262730; padding:15px; border-radius:10px;
                        border-left:4px solid {card['color']}; margin-bottom:12px;
                        min-height:120px;">
                <h4 style="margin:0 0 10px 0;">{card['icon']} {card['title']}</h4>
                <p style="color:#ccc; font-size:0.9em; margin:0;">{content_html}</p>
            </div>
            """, unsafe_allow_html=True)
