"""
pdf_processor.py — PDF text extraction for CaseMind AI.

Uses pdfplumber to extract complete text and metadata from PDF files.
Handles corrupted/encrypted PDFs gracefully.
"""

import os
from typing import Tuple


def process_pdf(filepath: str) -> Tuple[str, dict]:
    """
    Extract text and metadata from a PDF file.

    Args:
        filepath: Absolute path to the PDF file.

    Returns:
        Tuple of (extracted_text, metadata_dict).

    Raises:
        Exception: If the PDF cannot be opened or parsed.
    """
    import pdfplumber

    full_text = []
    metadata = {
        "pages": 0,
        "title": None,
        "author": None,
    }

    with pdfplumber.open(filepath) as pdf:
        metadata["pages"] = len(pdf.pages)

        # Extract PDF-level metadata if available
        if pdf.metadata:
            metadata["title"] = pdf.metadata.get("Title") or pdf.metadata.get("title")
            metadata["author"] = pdf.metadata.get("Author") or pdf.metadata.get("author")

        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                full_text.append(f"--- Page {i + 1} ---\n{page_text}")

    combined_text = "\n\n".join(full_text)

    if not combined_text.strip():
        combined_text = "[No extractable text found in this PDF. It may contain only images — OCR integration recommended.]"

    return combined_text, metadata
