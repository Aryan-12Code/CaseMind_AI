"""
email_processor.py — EML email text extraction for CaseMind AI.

Uses Python's built-in email module to extract sender, receiver,
subject, date, and body from .eml files.
"""

import email
from email import policy
from typing import Tuple


def process_eml(filepath: str) -> Tuple[str, dict]:
    """
    Parse an .eml file and extract structured email content.

    Args:
        filepath: Absolute path to the .eml file.

    Returns:
        Tuple of (extracted_text, metadata_dict).
        metadata contains: from, to, subject, date.

    Raises:
        Exception: If the email file cannot be parsed.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        msg = email.message_from_file(f, policy=policy.default)

    sender = msg.get("From", "Unknown")
    receiver = msg.get("To", "Unknown")
    subject = msg.get("Subject", "(No Subject)")
    date = msg.get("Date", "Unknown")

    metadata = {
        "from": sender,
        "to": receiver,
        "subject": subject,
        "date": date,
    }

    # Extract body content
    body = ""
    body_part = msg.get_body(preferencelist=("plain", "html"))
    if body_part:
        body = body_part.get_content()

    # Build a structured text representation
    lines = [
        f"From: {sender}",
        f"To: {receiver}",
        f"Subject: {subject}",
        f"Date: {date}",
        "",
        "--- Email Body ---",
        body if body else "[No body content found]",
    ]

    combined_text = "\n".join(lines)
    return combined_text, metadata
