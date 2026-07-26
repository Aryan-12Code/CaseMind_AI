"""
entity_extractor.py — Named Entity Recognition for CaseMind AI.

Uses spaCy (en_core_web_sm) to extract named entities from raw text:
  - PERSON (people's names)
  - ORG (organizations)
  - GPE (geopolitical entities / locations)
  - DATE (date expressions)
  - MONEY (monetary values)
"""

from typing import Optional
import streamlit as st
import re

from modules.entity_normalizer import clean_entity_name


@st.cache_resource
def _get_nlp():
    """
    Load the spaCy model lazily. Returns None if the model is not installed.
    """
    try:
        import spacy
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            import spacy.cli
            # Suppress output during download to keep logs clean
            spacy.cli.download("en_core_web_sm")
            return spacy.load("en_core_web_sm")
    except ImportError:
        return None
    except Exception as e:
        print(f"Failed to load or download spaCy model: {e}")
        return None


def extract_entities(text: str) -> dict[str, list[str]]:
    """
    Extract named entities from text using spaCy NER.

    Args:
        text: The raw text to analyze.

    Returns:
        Dictionary mapping entity type to list of unique values.
        Keys: persons, organizations, locations, dates, money.
        Returns empty lists if spaCy model is unavailable.
    """
    empty_result = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "money": [],
    }

    if not text or not text.strip():
        return empty_result

    nlp = _get_nlp()
    if nlp is None:
        return empty_result

    # spaCy has a max length limit; truncate very large texts
    max_chars = 100_000
    if len(text) > max_chars:
        text = text[:max_chars]

    doc = nlp(text)

    # Map spaCy label names to our output keys
    label_map = {
        "PERSON": "persons",
        "ORG": "organizations",
        "GPE": "locations",
        "LOC": "locations",
        "DATE": "dates",
        "MONEY": "money",
    }

    results: dict[str, list[str]] = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "money": [],
    }

    seen: dict[str, set[str]] = {k: set() for k in results}  # lowercase keys for dedup

    # Keywords that often trick the small NER model into thinking it's a person
    invalid_person_keywords = [
        "password", "meeting", "sender", "recipient", "invoice", 
        "transaction", "user", "admin", "unknown", "server", "date", 
        "row", "amount", "description", "id", "confidential",
        "ai", "ocr", "pdf", "csv", "drive", "casemind"
    ]

    for ent in doc.ents:
        key = label_map.get(ent.label_)
        if key is None:
            continue
            
        cleaned = ent.text.strip()
        
        # Remove timestamps like '21:20 ' or '14:30:00' from the entity
        cleaned = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?\b', '', cleaned).strip()
        
        # Apply strict filtering for persons
        if key == "persons":
            cleaned_lower = cleaned.lower()
            if any(kw in cleaned_lower for kw in invalid_person_keywords):
                continue
            # Ignore single letters or purely numeric "persons"
            if len(cleaned) <= 1 or cleaned.isnumeric():
                continue
                
        cleaned = clean_entity_name(cleaned)
        if not cleaned:
            continue

        dedup_key = cleaned.lower()
        if dedup_key not in seen[key]:
            seen[key].add(dedup_key)
            results[key].append(cleaned)

    return results


def count_total_entities(entities: dict[str, list[str]]) -> int:
    """Return the total count of all extracted entities."""
    return sum(len(v) for v in entities.values())
