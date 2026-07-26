"""
keyword_extractor.py — Regex-based keyword extraction for CaseMind AI.

Extracts structured data patterns from raw text without AI:
  - Email addresses
  - Phone numbers
  - Dates (multiple formats)
  - Currency values
  - URLs
  - Standalone numbers
"""

import re
from typing import Optional


# ── Compiled regex patterns ──────────────────────────────────────────────────

# Email addresses
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

# Phone numbers (various formats: +1-234-567-8900, (123) 456-7890, 123.456.7890, etc.)
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"
)

# Dates (DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD, Month DD YYYY, etc.)
_DATE_RE = re.compile(
    r"\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b"
    r"|\b\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}\b"
    r"|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{1,2},?\s+\d{2,4}\b",
    re.IGNORECASE,
)

# Currency values ($1,234.56, USD 1234, €500, ₹1000, £99.99)
_CURRENCY_RE = re.compile(
    r"[$€£₹¥]\s?\d[\d,]*\.?\d*"
    r"|\b(?:USD|EUR|GBP|INR|JPY)\s?\d[\d,]*\.?\d*\b",
    re.IGNORECASE,
)

# URLs (http, https, ftp, www)
_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
)

# Standalone numbers (integers and decimals, excluding dates and phone-like patterns)
_NUMBER_RE = re.compile(
    r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|\b\d+\.?\d*\b"
)


def extract_keywords(text: str) -> dict[str, list[str]]:
    """
    Extract structured keyword patterns from raw text.

    Args:
        text: The raw text to analyze.

    Returns:
        Dictionary mapping category names to lists of matched values.
        Categories: emails, phone_numbers, dates, currency, urls, numbers.
    """
    if not text or not text.strip():
        return {
            "emails": [],
            "phone_numbers": [],
            "dates": [],
            "currency": [],
            "urls": [],
            "numbers": [],
        }

    emails = _deduplicate(_EMAIL_RE.findall(text))
    phone_numbers = _deduplicate(_PHONE_RE.findall(text))
    dates = _deduplicate(_DATE_RE.findall(text))
    currency = _deduplicate(_CURRENCY_RE.findall(text))
    urls = _deduplicate(_URL_RE.findall(text))

    # For numbers, exclude values already captured by other patterns
    raw_numbers = _NUMBER_RE.findall(text)
    # Filter out numbers that are part of phone numbers or dates
    excluded = set()
    for p in phone_numbers:
        excluded.update(re.findall(r"\d+", p))
    for d in dates:
        excluded.update(re.findall(r"\d+", d))

    numbers = _deduplicate([n for n in raw_numbers if n not in excluded and len(n) <= 15])

    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "dates": dates,
        "currency": currency,
        "urls": urls,
        "numbers": numbers[:50],  # Cap numbers to avoid noise
    }


def _deduplicate(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in items:
        cleaned = item.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result
