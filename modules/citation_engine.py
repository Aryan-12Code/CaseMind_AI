"""
citation_engine.py — Evidence context builder for CaseMind AI.

Gathers all processed evidence text from the database, formats it
with source filenames for the AI to cite, and handles truncation
for large evidence sets.
"""

from modules.database import get_all_evidence, get_processed_by_evidence_id


# Maximum characters to send to the AI (Gemini flash supports ~1M tokens,
# but we cap at 80K chars for speed and cost efficiency)
MAX_CONTEXT_CHARS = 80_000


def build_evidence_context() -> str:
    """
    Gather all processed evidence text, formatted with source markers.

    Each file's text is wrapped with clear delimiters so the AI can
    cite the exact source filename in its responses.

    Returns:
        A single string with all evidence, ready to be sent to the AI.
        Returns empty string if no processed evidence exists.
    """
    all_evidence = get_all_evidence()
    if not all_evidence:
        return ""

    sections = []
    total_chars = 0

    for evidence in all_evidence:
        processed = get_processed_by_evidence_id(evidence["id"])
        if not processed or processed["processing_status"] != "Completed":
            continue

        raw_text = processed.get("raw_text", "")
        if not raw_text.strip():
            continue

        filename = evidence["filename"]
        filetype = evidence["filetype"].upper()

        # Format the section with clear source markers
        section = (
            f"\n[SOURCE: {filename} | Type: {filetype}]\n"
            f"{raw_text}\n"
            f"[END OF: {filename}]\n"
        )

        # Check if adding this section would exceed the limit
        if total_chars + len(section) > MAX_CONTEXT_CHARS:
            # Truncate this section to fit
            remaining = MAX_CONTEXT_CHARS - total_chars
            if remaining > 200:  # Only include if we can fit meaningful content
                truncated_text = raw_text[:remaining - 100]
                section = (
                    f"\n[SOURCE: {filename} | Type: {filetype}]\n"
                    f"{truncated_text}\n"
                    f"[TRUNCATED — File continues beyond context limit]\n"
                    f"[END OF: {filename}]\n"
                )
                sections.append(section)
            break

        sections.append(section)
        total_chars += len(section)

    if not sections:
        return ""

    header = (
        f"=== INVESTIGATION EVIDENCE ({len(sections)} files) ===\n"
        f"Total context: {total_chars:,} characters\n"
    )

    return header + "\n".join(sections)


def get_evidence_file_list() -> list[dict]:
    """
    Get a lightweight list of all evidence files with their processing status.

    Returns:
        List of dicts with: filename, filetype, has_text, char_count.
    """
    all_evidence = get_all_evidence()
    file_list = []

    for evidence in all_evidence:
        processed = get_processed_by_evidence_id(evidence["id"])
        has_text = False
        char_count = 0

        if processed and processed["processing_status"] == "Completed":
            text = processed.get("raw_text", "")
            has_text = bool(text.strip())
            char_count = len(text)

        file_list.append({
            "filename": evidence["filename"],
            "filetype": evidence["filetype"],
            "has_text": has_text,
            "char_count": char_count,
        })

    return file_list
