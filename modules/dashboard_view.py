"""
dashboard_view.py — Dashboard page for CaseMind AI.

Displays live metrics, recent activity, "Analyze Evidence" button for
AI case summary generation, and AI insights panel.
"""

import streamlit as st
import pandas as pd
from modules.database import init_db, get_dashboard_metrics, get_all_evidence
from modules.file_utils import format_filesize
from modules.chart_generator import _get_all_entities_and_keywords


def render() -> None:
    """Render the Dashboard page with live metrics, AI summary, and insights."""
    init_db()

    st.title("🏠 Dashboard")
    st.subheader("Intelligent Digital Evidence Investigation System")
    st.write("A modern, premium platform for analyzing digital evidence, "
             "mapping relationships, and generating comprehensive investigation reports.")
    st.markdown("---")

    # ── Live metric cards — Row 1: Evidence Overview ─────────────────────────
    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Evidence", value=f"{metrics['total_evidence']:,}")
    with col2:
        st.metric(label="Total PDFs", value=f"{metrics['total_pdfs']:,}")
    with col3:
        st.metric(label="Total Images", value=f"{metrics['total_images']:,}")
    with col4:
        st.metric(label="Storage Used", value=format_filesize(metrics["storage_used_bytes"]))

    st.write("")

    # ── Live metric cards — Row 2: Entity & Keyword Stats ────────────────────
    entities, keywords = _get_all_entities_and_keywords()
    
    total_people = len(set(entities.get("persons", [])))
    total_orgs = len(set(entities.get("organizations", [])))
    total_locs = len(set(entities.get("locations", [])))
    total_money = len(keywords.get("currency", []))
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(label="People Detected", value=f"{total_people:,}")
    with col6:
        st.metric(label="Organizations", value=f"{total_orgs:,}")
    with col7:
        st.metric(label="Locations", value=f"{total_locs:,}")
    with col8:
        st.metric(label="Money Transactions", value=f"{total_money:,}")

    st.markdown("---")

    # ── AI Analysis Section ──────────────────────────────────────────────────
    _render_ai_analysis_section()

    st.markdown("---")

    # ── Recent Activity ──────────────────────────────────────────────────────
    st.subheader("🕒 Recent Activity")

    all_evidence = get_all_evidence()

    if all_evidence:
        recent = all_evidence[:10]
        activity_data = [
            {
                "Time": e["upload_time"],
                "Action": f"Uploaded {e['filename']}",
                "Type": e["filetype"].upper(),
                "Size": format_filesize(e["filesize"]),
                "Status": f"✓ {e['status']}",
            }
            for e in recent
        ]
        st.dataframe(
            pd.DataFrame(activity_data),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No activity yet. Upload evidence to see activity here.")


def _render_ai_analysis_section() -> None:
    """Render the AI case analysis section with summary and insights."""
    api_key = st.session_state.get("groq_api_key", "")

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader("🔍 AI Case Analysis")
    with col_btn:
        analyze_clicked = st.button(
            "🧠 Analyze Evidence",
            type="primary",
            use_container_width=True,
            disabled=not api_key,
        )

    if not api_key:
        st.info("💡 Set your Groq API key in **Settings** to enable AI analysis.")
        return

    # Generate summary when button is clicked
    if analyze_clicked:
        _run_analysis(api_key)

    # Display cached summary if available
    if "case_summary" in st.session_state and st.session_state.case_summary:
        from modules.summary_generator import render_summary_cards, render_suggested_questions
        render_summary_cards(st.session_state.case_summary)

        st.markdown("---")

        # Suggested questions
        clicked_q = render_suggested_questions(st.session_state.case_summary)
        if clicked_q:
            st.session_state["chat_prefill"] = clicked_q
            st.info(f"💬 Go to **AI Chat** to see the answer for: \"{clicked_q}\"")

        st.markdown("---")

        # AI Insights
        if "ai_insights_rendered" not in st.session_state:
            st.session_state.ai_insights_rendered = False

        if st.button("🧠 Generate AI Insights", use_container_width=False):
            with st.spinner("🔍 Generating insights..."):
                from modules.insight_generator import generate_and_render_insights
                generate_and_render_insights(api_key)
                st.session_state.ai_insights_rendered = True

        # Removed old export buttons (moved to Investigation Reports page)
        st.markdown("---")


def _run_analysis(api_key: str) -> None:
    """Run the full AI case analysis with loading animations."""
    from modules.summary_generator import generate_full_summary

    progress = st.progress(0, text="🔍 Analyzing Evidence...")
    progress.progress(20, text="📂 Searching Documents...")

    summary = generate_full_summary(api_key)

    progress.progress(70, text="🧠 Generating Investigation Summary...")

    if summary:
        st.session_state.case_summary = summary
        # Store suggested questions for the chat page
        if "suggested_questions" in summary:
            st.session_state["ai_suggestions"] = summary["suggested_questions"]
        progress.progress(100, text="✅ Analysis Complete!")
    else:
        progress.progress(100, text="⚠️ Analysis could not be completed.")

    progress.empty()
    st.rerun()



