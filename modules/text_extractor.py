"""
text_extractor.py — Central text extraction orchestrator for CaseMind AI.

Dispatches to the correct processor based on file type and wraps
all calls in robust error handling to prevent crashes.
"""

import time
from typing import Optional
from modules.pdf_processor import process_pdf
from modules.image_processor import process_image
from modules.csv_processor import process_csv
from modules.email_processor import process_eml


def extract_text(filepath: str, filetype: str) -> dict:
    """
    Extract text from a file by dispatching to the appropriate processor.

    Args:
        filepath: Absolute path to the file.
        filetype: Lowercase file extension (e.g. 'pdf', 'txt', 'png').

    Returns:
        Dictionary with keys:
            - raw_text (str): The extracted text content.
            - metadata (dict): File-type-specific metadata.
            - status (str): 'Completed' or 'Failed'.
            - error (str | None): Error message if processing failed.
            - processing_time (float): Seconds taken to process.
    """
    start_time = time.time()

    result = {
        "raw_text": "",
        "metadata": {},
        "status": "Completed",
        "error": None,
        "processing_time": 0.0,
    }

    try:
        if filetype == "pdf":
            text, meta = process_pdf(filepath)
        elif filetype in ("png", "jpg", "jpeg"):
            text, meta = process_image(filepath)
        elif filetype == "csv":
            text, meta = process_csv(filepath)
        elif filetype == "eml":
            text, meta = process_eml(filepath)
        elif filetype == "txt":
            text, meta = _process_txt(filepath)
        else:
            text = ""
            meta = {}
            result["status"] = "Failed"
            result["error"] = f"Unsupported file type for processing: {filetype}"

        if result["status"] != "Failed":
            result["raw_text"] = text
            result["metadata"] = meta

    except Exception as e:
        result["status"] = "Failed"
        result["error"] = str(e)

    result["processing_time"] = round(time.time() - start_time, 3)
    return result


def _process_txt(filepath: str) -> tuple[str, dict]:
    """
    Read a plain text file while preserving formatting.

    Returns:
        Tuple of (full_text, metadata_dict).
    """
    import os

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    line_count = content.count("\n") + 1 if content else 0
    char_count = len(content)

    metadata = {
        "line_count": line_count,
        "char_count": char_count,
        "filesize_bytes": os.path.getsize(filepath),
    }

    return content, metadata
