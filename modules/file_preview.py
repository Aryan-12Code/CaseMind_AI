"""
file_preview.py — File preview rendering for CaseMind AI.

Displays inline previews for supported file types (TXT, CSV, PDF, Image, EML)
using Streamlit components.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional


def render_preview(filepath: str, filetype: str) -> None:
    """
    Render an inline preview of a file based on its type.

    Args:
        filepath: Absolute path to the file on disk.
        filetype: Lowercase file extension (e.g. 'txt', 'csv', 'png').
    """
    if not os.path.exists(filepath):
        st.error("⚠️ File not found on disk. It may have been moved or deleted.")
        return

    try:
        if filetype == "txt":
            _preview_text(filepath)
        elif filetype == "csv":
            _preview_csv(filepath)
        elif filetype in ("png", "jpg", "jpeg"):
            _preview_image(filepath)
        elif filetype == "pdf":
            _preview_pdf(filepath)
        elif filetype == "eml":
            _preview_eml(filepath)
        else:
            st.info(f"Preview is not available for `.{filetype}` files.")
    except Exception as e:
        st.error(f"❌ Error rendering preview: {e}")


def _preview_text(filepath: str) -> None:
    """Display text file contents in a code block."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(10_000)  # Limit to first 10k chars
    st.code(content, language="text")
    if os.path.getsize(filepath) > 10_000:
        st.caption("ℹ️ Showing first 10,000 characters only.")


def _preview_csv(filepath: str) -> None:
    """Display CSV file as an interactive dataframe."""
    try:
        df = pd.read_csv(filepath, nrows=100)
        st.dataframe(df, use_container_width=True, hide_index=True)
        total_rows = sum(1 for _ in open(filepath, encoding="utf-8", errors="replace")) - 1
        if total_rows > 100:
            st.caption(f"ℹ️ Showing first 100 of {total_rows} rows.")
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")


def _preview_image(filepath: str) -> None:
    """Display image file."""
    st.image(filepath, use_container_width=True)


def _preview_pdf(filepath: str) -> None:
    """Display a placeholder for PDF preview (full rendering requires extra libs)."""
    file_size = os.path.getsize(filepath)
    st.markdown(f"""
    <div style="background-color: #262730; padding: 40px; border-radius: 10px;
                text-align: center; border: 1px solid #444;">
        <h3>📄 PDF Document</h3>
        <p style="color: #bbb;">File: {os.path.basename(filepath)}</p>
        <p style="color: #888;">Size: {file_size / 1024:.1f} KB</p>
        <p style="color: #666; font-size: 0.9em;">
            Full PDF preview will be available after OCR integration.<br/>
            Use the Download button to view the complete document.
        </p>
    </div>
    """, unsafe_allow_html=True)


def _preview_eml(filepath: str) -> None:
    """Display EML email body as plain text."""
    import email
    from email import policy

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        msg = email.message_from_file(f, policy=policy.default)

    # Display headers
    st.markdown("**From:** " + (msg.get("From", "Unknown")))
    st.markdown("**To:** " + (msg.get("To", "Unknown")))
    st.markdown("**Subject:** " + (msg.get("Subject", "(No Subject)")))
    st.markdown("**Date:** " + (msg.get("Date", "Unknown")))
    st.markdown("---")

    # Display body
    body = msg.get_body(preferencelist=("plain", "html"))
    if body:
        content = body.get_content()
        st.code(content[:10_000], language="text")
    else:
        st.info("No readable body content found in this email.")
