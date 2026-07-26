"""
about_view.py — About page for CaseMind AI.

Displays project information, tech stack, and version details.
"""

import streamlit as st


def render() -> None:
    """Render the About page."""
    st.title("ℹ️ About CaseMind AI")
    st.markdown("---")
    
    st.markdown("""
    ### 🛡️ CaseMind AI
    **Version:** 1.0.0 (Production Build)
    
    CaseMind AI is a professional, intelligent digital evidence investigation platform designed to streamline the analysis of unstructured data. It combines traditional file parsing (OCR, PDF extraction) with advanced Natural Language Processing (NLP) and the Groq AI Engine to uncover relationships, identify high-risk individuals, and summarize complex cases automatically.
    
    ---
    
    ### 💻 Technology Stack
    
    **Frontend & UI**
    - Streamlit (Core framework)
    - Plotly (Interactive analytics)
    - PyVis & NetworkX (Relationship graphing)
    
    **Backend & Storage**
    - Python 3.10+
    - Streamlit (Frontend & State Management)
    - Groq Engine (Generative AI)
    - spaCy (NLP & Entity Extraction)
    - EasyOCR (Optical Character Recognition)
    - pdfplumber (PDF text extraction)
    
    ---
    
    ### 🔒 Security & Privacy
    All evidence processing occurs strictly within isolated case environments. Raw text and extracted entities are stored locally in the case-specific SQLite database. Data is only sent to the configured AI provider during active querying or summary generation.
    """)
