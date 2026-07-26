"""
dashboard_export.py — Professional PDF report generation for CaseMind AI.

Generates a multi-page PDF containing Cover Page, Executive Summary,
Suspicion Scores, and embedded Plotly charts.
"""

from fpdf import FPDF
from modules.database import get_dashboard_metrics
from modules.suspicion_score import generate_suspicion_scores
import modules.chart_generator as cg
import tempfile
import os
from datetime import datetime
import streamlit as st


def generate_dashboard_pdf(case_name: str, summary_data: dict = None) -> bytes:
    """
    Generate a professional multi-page PDF report.
    """
    metrics = get_dashboard_metrics()
    suspects = generate_suspicion_scores()
    now = datetime.now().strftime("%Y-%m-%d")
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ── Page 1: Cover Page ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(50)
    pdf.cell(0, 15, "CaseMind AI", ln=True, align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Professional Investigation Report", ln=True, align="C")
    pdf.ln(20)
    
    pdf.set_font("Helvetica", "B", 14)
    safe_case_name = case_name.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 10, f"Case Name: {safe_case_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Date Generated: {now}", ln=True, align="C")
    
    # Check for company name in settings
    company_name = st.session_state.get("company_name", "")
    if company_name:
        pdf.ln(20)
        pdf.set_font("Helvetica", "I", 12)
        safe_company = company_name.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(0, 8, f"Prepared by: {safe_company}", ln=True, align="C")
        
    # ── Page 2: Executive Summary ────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Executive Summary", ln=True)
    pdf.ln(5)
    
    if summary_data and "case_summary" in summary_data:
        pdf.set_font("Helvetica", "", 11)
        safe_text = summary_data["case_summary"].encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text)
    else:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 6, "No AI Summary generated yet. Run 'Analyze Evidence' to include it.", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Evidence Overview", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"- Total Evidence Files: {metrics.get('total_evidence', 0)}", ln=True)
    pdf.cell(0, 8, f"- Processed Files: {metrics.get('processed_files', 0)}", ln=True)
    pdf.cell(0, 8, f"- Total Entities Extracted: {metrics.get('total_entities', 0)}", ln=True)
    
    # ── Page 3: High Risk Individuals ────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "High Risk Individuals (Suspicion Scores)", ln=True)
    pdf.ln(5)
    
    if suspects:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(70, 8, "Person Name", border=1)
        pdf.cell(30, 8, "Risk Level", border=1, align="C")
        pdf.cell(25, 8, "Score %", border=1, align="C")
        pdf.cell(65, 8, "Top Reason", border=1)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 10)
        for s in suspects[:20]:
            name = s["name"].encode("latin-1", "replace").decode("latin-1")
            reason = s["reasons"][0] if s["reasons"] else "None"
            reason = reason.encode("latin-1", "replace").decode("latin-1")
            
            pdf.cell(70, 8, name[:35], border=1)
            pdf.cell(30, 8, s["risk_level"], border=1, align="C")
            pdf.cell(25, 8, f"{s['percentage']}%", border=1, align="C")
            pdf.cell(65, 8, reason[:35], border=1)
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "No persons detected or scored yet.", ln=True)

    # ── Page 4: Analytics Charts (if kaleido is working) ─────────────────────
    try:
        import kaleido
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Investigation Analytics", ln=True)
        pdf.ln(5)
        
        # Save charts to temp files and embed
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "pie.png")
            fig1 = cg.get_entity_distribution_pie()
            # Fix layout for static image (light bg)
            fig1.update_layout(paper_bgcolor="white", plot_bgcolor="white", font=dict(color="black"))
            fig1.write_image(f1, width=600, height=400)
            
            f2 = os.path.join(tmpdir, "bar.png")
            fig2 = cg.get_most_mentioned_people_bar()
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white", font=dict(color="black"))
            fig2.write_image(f2, width=600, height=400)
            
            pdf.image(f1, w=150)
            pdf.ln(10)
            pdf.image(f2, w=150)
            
    except Exception as e:
        # If kaleido fails or is missing, skip charts gracefully
        pass
        
    return bytes(pdf.output())
