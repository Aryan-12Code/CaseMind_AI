"""
entity_explorer_view.py — Entity Explorer page for CaseMind AI.

Dedicated page to browse and inspect all extracted entities 
(Persons, Organizations, Locations, etc).
"""

import streamlit as st
import pandas as pd
from modules.database import init_db
from modules.chart_generator import _get_all_entities_and_keywords
from collections import Counter


def render() -> None:
    """Render the Entity Explorer page."""
    init_db()

    st.title("🗂️ Entity Explorer")
    st.write("Browse and search all entities automatically extracted from the evidence.")
    st.markdown("---")
    
    entities, _ = _get_all_entities_and_keywords()
    
    # ── Sidebar Selection ────────────────────────────────────────────────────
    entity_type = st.radio(
        "Select Entity Type",
        ["Persons", "Organizations", "Locations", "Dates", "Money"],
        horizontal=True
    )
    
    key = entity_type.lower()
    items = entities.get(key, [])
    
    if not items:
        st.info(f"No {entity_type.lower()} have been detected in the processed evidence yet.")
        return
        
    counts = Counter(items)
    df = pd.DataFrame(counts.items(), columns=["Entity", "Mentions"]).sort_values("Mentions", ascending=False)
    
    st.subheader(f"Total Unique {entity_type}: {len(counts)}")
    
    # ── Search & Filter ──────────────────────────────────────────────────────
    search = st.text_input(f"Search {entity_type}...", "")
    if search:
        df = df[df["Entity"].str.contains(search, case=False, na=False)]
        
    # ── Layout: List vs Details ──────────────────────────────────────────────
    col_list, col_details = st.columns([1, 2])
    
    with col_list:
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
        
    with col_details:
        st.markdown("### 🔍 Inspector")
        st.write("Use the **Search** box and select a row in the table to find specific entities.")
        st.info("Tip: Head over to **AI Chat** to ask specific questions about any of these entities. The AI will pull up the exact documents where they are mentioned.")
        
        # In a real app, we would use st.dataframe selection events (requires newer streamlit versions)
        # For now, we provide a quick search to isolate context
        selected = st.selectbox("Select entity to inspect:", df["Entity"].tolist())
        
        if selected:
            st.markdown(f"#### Inspecting: `{selected}`")
            st.metric("Total Mentions", counts[selected])
            st.write("This entity was extracted directly from the raw text by the NLP engine. View the **Relationship Graph** to see how it connects to other entities in the case.")
