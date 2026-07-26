"""
graph_view.py — Orchestrator for the Entity Profile Cards page.
"""

import streamlit as st
from modules.database import init_db
from modules.relationship_builder import build_entity_dossiers

def render() -> None:
    """Render the Entity Profile Cards page."""
    init_db()

    st.title("📇 Entity Profiles")
    st.write("Structured dossiers of all key individuals, their connections, and their footprints across the evidence.")
    st.markdown("---")

    with st.spinner("Compiling dossiers..."):
        dossiers = build_entity_dossiers()
        
    if not dossiers:
        st.info("No entities found in the current evidence. Please upload and process documents first.")
        return

    # Add a simple text search filter
    search_query = st.text_input("🔍 Search Entities", placeholder="Type a name to filter...").lower()
    
    # Filter dossiers
    filtered_dossiers = [d for d in dossiers if search_query in d["name"].lower()]
    
    if not filtered_dossiers:
        st.warning("No entities match your search.")
        return
        
    # Render in a responsive grid
    cols = st.columns(3)
    
    for i, d in enumerate(filtered_dossiers):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.subheader(d["name"])
                st.markdown("---")
                
                st.markdown(f"**Role:** {d['role']}")
                
                st.markdown("**Connected People:**")
                if d["connected_people"]:
                    for p in d["connected_people"]:
                        st.markdown(f"- {p}")
                else:
                    st.write("*None found*")
                    
                st.markdown("**Locations:**")
                if d["locations"]:
                    for loc in d["locations"]:
                        st.markdown(f"- {loc}")
                else:
                    st.write("*None found*")
                    
                st.markdown("**Documents:**")
                if d["documents"]:
                    for doc in d["documents"]:
                        st.markdown(f"- `{doc}`")
                else:
                    st.write("*None found*")
                    
                st.markdown("**Money:**")
                if d["money"]:
                    for money in d["money"]:
                        st.markdown(f"- {money}")
                else:
                    st.write("*None found*")
                    
                st.markdown("---")
                st.metric("Mention Count", d["mentions"])
