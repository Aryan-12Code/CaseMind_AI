"""
entity_normalizer.py — Cleans, filters, and resolves entities for the Relationship Graph.
"""

import re

# Strict blacklist for completely dropping technical nodes
TECHNICAL_BLACKLIST = {
    "ai", "ocr", "pdf", "csv", "txt", "eml", "jpg", "jpeg", "png", "drive",
    "casemind", "casemind ai", "readme", "readme.txt", "system", "database",
    "processor", "extractor", "model", "algorithm", "module", "node", "edge",
    "unknown", "admin", "user", "sender", "recipient", "invoice", "transaction",
    "date", "row", "amount", "description", "id", "confidential"
}

def clean_entity_name(name: str) -> str:
    """Normalize whitespace, capitalization, punctuation, and remove timestamps."""
    # Strip timestamps (e.g. 21:20)
    cleaned = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?\b', '', name)
    # Replace punctuation with spaces so "Sharma, Rahul" -> "Sharma Rahul"
    cleaned = re.sub(r"[^\w\s'-]", " ", cleaned)
    # Strip multiple spaces and trim
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # Normalize capitalization (Title Case)
    return cleaned.title()

def truncate_label(name: str, max_len: int = 15) -> str:
    """Truncate long labels, mostly used for documents."""
    if len(name) > max_len:
        return name[:max_len] + "..."
    return name

def is_valid_entity(name: str) -> bool:
    """Check if the entity is valid (not a technical term, not empty)."""
    if not name or len(name) <= 1:
        return False
    if name.lower() in TECHNICAL_BLACKLIST:
        return False
    return True

def resolve_duplicates(entities: list[str]) -> dict[str, str]:
    """
    Map variant person names to a single canonical name.
    e.g. 'Aman' -> 'Aman Verma', 'Sharma Rahul' -> 'Rahul Sharma'
    """
    unique_ents = list(set(entities))
    resolved = {ent: ent for ent in unique_ents}

    # Cluster names that share tokens (first name vs full name, reordered names).
    groups: dict[frozenset[str], list[str]] = {}
    for ent in unique_ents:
        tokens = frozenset(ent.lower().split())
        if not tokens:
            continue

        merged_key = None
        for existing_tokens in list(groups.keys()):
            if tokens <= existing_tokens or existing_tokens <= tokens:
                merged_key = existing_tokens | tokens
                groups[merged_key] = groups.pop(existing_tokens) + [ent]
                break

        if merged_key is None:
            groups[tokens] = [ent]

    for names in groups.values():
        canonical = max(names, key=lambda n: (len(n.split()), len(n)))
        for name in names:
            resolved[name] = canonical

    return resolved
