"""
search_engine.py — Global full-text search across processed evidence for CaseMind AI.

Searches all ProcessedEvidence.raw_text records and returns
matching snippets with highlighted keywords.
"""

import re
from typing import Optional
from modules.database import search_processed_text


def global_search(query: str, max_results: int = 50) -> list[dict]:
    """
    Search across all processed evidence text for a keyword.

    Args:
        query: The search term (case-insensitive).
        max_results: Maximum number of results to return.

    Returns:
        List of dicts, each containing:
            - evidence_id (int)
            - filename (str)
            - filetype (str)
            - snippet (str): Surrounding context with the match.
            - line_number (int | None): Approximate line of the match.
    """
    if not query or not query.strip():
        return []

    query = query.strip()
    raw_results = search_processed_text(query)
    matches = []

    for row in raw_results:
        text = row["raw_text"]
        snippets = _find_snippets(text, query)

        for snippet, line_num in snippets:
            matches.append({
                "evidence_id": row["evidence_id"],
                "filename": row["filename"],
                "filetype": row["filetype"],
                "snippet": snippet,
                "line_number": line_num,
            })

            if len(matches) >= max_results:
                return matches

    return matches


def _find_snippets(text: str, query: str, context_chars: int = 120) -> list[tuple[str, int]]:
    """
    Find all occurrences of query in text and return surrounding snippets.

    Returns:
        List of (snippet_string, approximate_line_number) tuples.
    """
    results = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    lines = text.split("\n")

    # Build a line index map (char position -> line number)
    line_starts = []
    pos = 0
    for i, line in enumerate(lines):
        line_starts.append(pos)
        pos += len(line) + 1  # +1 for the newline

    for match in pattern.finditer(text):
        start = match.start()
        end = match.end()

        # Determine line number
        line_num = 1
        for i, ls in enumerate(line_starts):
            if ls > start:
                break
            line_num = i + 1

        # Extract context around the match
        snippet_start = max(0, start - context_chars)
        snippet_end = min(len(text), end + context_chars)
        snippet = text[snippet_start:snippet_end].strip()

        # Add ellipsis if truncated
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(text):
            snippet = snippet + "..."

        results.append((snippet, line_num))

    return results


def highlight_query(text: str, query: str) -> str:
    """
    Wrap occurrences of query in text with HTML <mark> tags for highlighting.

    Args:
        text: The text to highlight within.
        query: The search term.

    Returns:
        HTML string with matches wrapped in <mark> tags.
    """
    if not query:
        return text
    pattern = re.compile(f"({re.escape(query)})", re.IGNORECASE)
    return pattern.sub(r"<mark style='background-color:#0068c9;color:white;padding:1px 3px;border-radius:3px;'>\1</mark>", text)
