"""
image_processor.py — Image OCR text extraction for CaseMind AI.

Uses EasyOCR to extract readable text from PNG/JPG/JPEG images.
Returns extracted text and average confidence score.
"""

from typing import Tuple
import streamlit as st


@st.cache_resource
def _get_reader():
    """
    Get or create a cached EasyOCR Reader instance.
    Caching avoids reloading the model on every file upload.
    """
    import easyocr
    return easyocr.Reader(["en"], gpu=False, verbose=False)


def process_image(filepath: str) -> Tuple[str, dict]:
    """
    Extract text from an image using EasyOCR.

    Args:
        filepath: Absolute path to the image file.

    Returns:
        Tuple of (extracted_text, metadata_dict).
        metadata contains: confidence (average), detected_blocks (count).

    Raises:
        Exception: If the image cannot be read or processed.
    """
    reader = _get_reader()
    results = reader.readtext(filepath)

    metadata = {
        "detected_blocks": len(results),
        "confidence": 0.0,
    }

    if not results:
        return "[No text detected in this image.]", metadata

    # Extract text lines and compute average confidence
    text_lines = []
    total_confidence = 0.0

    for (bbox, text, confidence) in results:
        text_lines.append(text)
        total_confidence += confidence

    metadata["confidence"] = round(total_confidence / len(results), 4)

    combined_text = "\n".join(text_lines)
    return combined_text, metadata
