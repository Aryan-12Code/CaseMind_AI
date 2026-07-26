"""
keyword_analytics_view.py — Keyword Analytics page for CaseMind AI.

Searchable dashboard for deep-diving into extracted keywords
(Emails, Phones, Currency, URLs).
"""

import streamlit as st
import pandas as pd
from modules.database import init_db
from modules.chart_generator import _get_all_entities_and_keywords
from collections import Counter


def render() -> None:
    """Render the Keyword Analytics page."""
    init_db()

    st.title("🔑 Keyword Analytics")
    st.write("Explore specific structured data points extracted from the evidence.")
    st.markdown("---")
    
    _, keywords = _get_all_entities_and_keywords()
    
    # ── Sidebar Selection ────────────────────────────────────────────────────
    kw_type = st.radio(
        "Select Data Type",
        ["Emails", "Phone Numbers", "Currency", "URLs"],
        horizontal=True
    )
    
    key_map = {
        "Emails": "emails",
        "Phone Numbers": "phone_numbers",
        "Currency": "currency",
        "URLs": "urls"
    }
    
    key = key_map[kw_type]
    items = keywords.get(key, [])
    
    if not items:
        st.info(f"No {kw_type.lower()} have been detected in the processed evidence yet.")
        return
        
    counts = Counter(items)
    df = pd.DataFrame(counts.items(), columns=["Keyword", "Frequency"]).sort_values("Frequency", ascending=False)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Total Unique {kw_type}", len(counts))
    with col2:
        st.metric("Total Occurrences", len(items))
    with col3:
        top = df.iloc[0]["Keyword"] if not df.empty else "N/A"
        st.metric("Most Frequent", top)
        
    st.markdown("---")
        
    # ── Search & Filter ──────────────────────────────────────────────────────
    search = st.text_input(f"Search {kw_type}...", "")
    if search:
        df = df[df["Keyword"].str.contains(search, case=False, na=False)]
        
    st.dataframe(df, use_container_width=True, hide_index=True)
