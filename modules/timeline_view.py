"""
timeline_view.py — Investigation Timeline page for CaseMind AI.

Displays a chronological sequence of true events extracted from the evidence,
ignoring internal system logs unless explicitly toggled.
"""

import streamlit as st
from modules.database import init_db
from modules.timeline_generator import generate_timeline_events


def render() -> None:
    """Render the Timeline page."""
    init_db()

    st.title("🕒 Investigation Timeline")
    st.write("Chronological story of the case, built automatically from evidence footprints.")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        sort_order = st.selectbox("Sort Order", ["Oldest First", "Newest First"], index=0)
    with col3:
        st.write("") # spacing
        st.write("")
        show_system = st.checkbox("Show System Logs", value=False)
    
    st.markdown("---")

    # ── Render Timeline ──────────────────────────────────────────────────────
    with st.spinner("Compiling chronological events..."):
        events = generate_timeline_events(sort_order=sort_order, include_system_logs=show_system)
        
    if not events:
        st.info("No timeline events found. Upload evidence containing dates to build the timeline.")
        return
        
    st.caption(f"Found {len(events)} events in the timeline.")
    
    for i, event in enumerate(events):

        # Color coding: System logs are grey, investigation events are pink/primary
        border_color = "#555" if event.get('is_system_log') else "#E91E63"

        # Build optional metadata blocks if they exist
        meta_lines = []
        if not event.get('is_system_log'):
            if event.get('persons'):
                meta_lines.append(f"<div style='margin-top:5px'>👤 <b>Personnel:</b> {event['persons']}</div>")
            if event.get('locations'):
                meta_lines.append(f"<div style='margin-top:5px'>📍 <b>Location:</b> {event['locations']}</div>")
            if event.get('money'):
                meta_lines.append(f"<div style='margin-top:5px'>💰 <b>Amounts:</b> {event['money']}</div>")
        meta_html = "".join(meta_lines)
        margin = "8px" if meta_html else "0px"

        # Build HTML as explicit concatenation — NO indentation that markdown could misread
        card = ""
        card += f'<div style="background-color:#262730;padding:15px 20px;border-radius:10px;margin-bottom:10px;border-left:5px solid {border_color};box-shadow:0 4px 6px rgba(0,0,0,0.1)">'
        card += f'<div style="display:flex;justify-content:space-between">'
        card += f'<h4 style="margin:0;display:flex;align-items:center;gap:8px"><span style="font-size:1.2em">{event["icon"]}</span> {event["title"]}</h4>'
        card += f'<span style="color:{border_color};font-weight:bold;font-size:1.1em">{event["date_str"]}</span>'
        card += '</div>'
        card += f'<p style="color:#bbb;margin:12px 0 10px 0;font-size:1.05em">{event["desc"]}</p>'
        card += f'<div style="background-color:rgba(0,0,0,0.2);padding:10px;border-radius:5px;font-size:0.9em;color:#ddd">'
        card += meta_html
        card += f'<div style="margin-top:{margin};color:#888">📎 <b>Source Evidence:</b> <code>{event["source"]}</code></div>'
        card += '</div>'
        card += '</div>'

        st.markdown(card, unsafe_allow_html=True)

        # Add arrow between events, except for the last one
        if i < len(events) - 1:
            arrow = f'<div style="text-align:center;margin:5px 0"><span style="color:{border_color};font-size:1.5em;line-height:1">↓</span></div>'
            st.markdown(arrow, unsafe_allow_html=True)
