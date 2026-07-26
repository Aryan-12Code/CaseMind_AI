"""
reports_view.py — Investigation Reports & Exports for CaseMind AI.

Allows users to generate and download comprehensive reports 
and raw data exports for the current active case.
"""

import streamlit as st
from modules.database import init_db
from modules.cases_db import get_case_by_id
from modules.export_manager import (
    generate_export_csv,
    generate_export_excel,
    generate_export_json
)
from modules.dashboard_export import generate_dashboard_pdf


def render() -> None:
    """Render the Investigation Reports page."""
    init_db()

    st.title("📑 Investigation Reports & Exports")
    st.write("Generate professional reports and export case data for external analysis.")
    st.markdown("---")
    
    case_id = st.session_state.get("active_case_id")
    case_info = get_case_by_id(case_id) if case_id else None
    case_name = case_info["name"] if case_info else "CaseMind Investigation"

    col_reports, col_data = st.columns(2)
    
    # ── Professional Reports ─────────────────────────────────────────────────
    with col_reports:
        st.subheader("📄 Professional Reports")
        st.write("Generate a multi-page PDF summarizing the entire investigation.")
        
        st.markdown("""
        **Includes:**
        - Cover Page & Executive Summary
        - Processed Evidence Overview
        - Suspicion Score Leaderboard
        - Analytics Charts
        """)
        
        if st.button("Generate Professional PDF", type="primary", use_container_width=True):
            with st.spinner("Compiling PDF report (this may take a moment)..."):
                try:
                    summary = st.session_state.get("case_summary")
                    st.session_state["pdf_export"] = generate_dashboard_pdf(case_name, summary)
                    st.success("Report generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")

        if "pdf_export" in st.session_state:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=st.session_state["pdf_export"],
                file_name=f"{case_name.replace(' ', '_')}_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # ── Raw Data Exports ─────────────────────────────────────────────────────
    with col_data:
        st.subheader("💾 Raw Data Exports")
        st.write("Export processed evidence and analytics for use in other tools.")
        
        st.markdown("**Excel (Comprehensive)**")
        st.write("Includes multiple sheets: Evidence, Suspicion Scores, and Extracted Entities.")
        if st.button("Generate Excel Export", use_container_width=True):
            with st.spinner("Generating Excel workbook..."):
                try:
                    st.session_state["excel_export"] = generate_export_excel()
                    st.success("Excel generated successfully!")
                except Exception as e:
                    st.error(f"Excel export failed: {e}")
                    
        if "excel_export" in st.session_state:
            st.download_button(
                label="⬇️ Download Excel",
                data=st.session_state["excel_export"],
                file_name=f"{case_name.replace(' ', '_')}_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
                    
        st.markdown("---")
        
        col_csv, col_json = st.columns(2)
        with col_csv:
            st.markdown("**CSV**")
            st.write("Evidence list only.")
            if st.button("Generate CSV", use_container_width=True):
                st.session_state["csv_export"] = generate_export_csv()
            
            if "csv_export" in st.session_state:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=st.session_state["csv_export"],
                    file_name=f"{case_name.replace(' ', '_')}_Evidence.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col_json:
            st.markdown("**JSON**")
            st.write("Complete raw case dump.")
            if st.button("Generate JSON", use_container_width=True):
                st.session_state["json_export"] = generate_export_json()
                
            if "json_export" in st.session_state:
                st.download_button(
                    label="⬇️ Download JSON",
                    data=st.session_state["json_export"],
                    file_name=f"{case_name.replace(' ', '_')}_Dump.json",
                    mime="application/json",
                    use_container_width=True
                )
