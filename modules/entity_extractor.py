"""
entity_extractor.py — Named Entity Recognition for CaseMind AI.

Uses Groq LLM to accurately extract named entities from raw text:
  - PERSON (people's names)
  - ORG (organizations)
  - LOC (locations / geopolitical entities)
  - DATE (date expressions)
  - MONEY (monetary values)
"""

from typing import Optional
import json
import streamlit as st
from groq import Groq

from modules.entity_normalizer import clean_entity_name

def extract_entities(text: str, api_key: str = None) -> dict[str, list[str]]:
    """
    Extract named entities from text using Groq LLM.

    Args:
        text: The raw text to analyze.
        api_key: The Groq API key for authentication.

    Returns:
        Dictionary mapping entity type to list of unique values.
        Keys: persons, organizations, locations, dates, money.
        Returns empty lists if extraction fails or no api_key is provided.
    """
    empty_result = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "money": [],
    }

    if not text or not text.strip() or not api_key:
        return empty_result

    # Truncate text to avoid token limits (Groq handles ~6K words well in standard tiers)
    max_chars = 20_000
    if len(text) > max_chars:
        text = text[:max_chars]

    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""You are an expert intelligence analyst. Extract named entities from the following text and categorize them into: persons, organizations, locations, dates, and money.
        
Return ONLY a valid JSON object matching this schema exactly, with lists of unique strings. Ensure that you correctly classify locations vs persons.
{{
  "persons": [],
  "organizations": [],
  "locations": [],
  "dates": [],
  "money": []
}}
Do NOT include markdown formatting or backticks. Return the raw JSON object.

Text:
{text}
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        results = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "money": [],
        }
        
        # Ensure schema and clean names
        for key in results:
            if key in data and isinstance(data[key], list):
                seen = set()
                for item in data[key]:
                    if isinstance(item, str) and item.strip():
                        cleaned = clean_entity_name(item.strip())
                        if cleaned:
                            lower_key = cleaned.lower()
                            if lower_key not in seen:
                                seen.add(lower_key)
                                results[key].append(cleaned)
                                
        return results
        
    except Exception as e:
        print(f"Groq Entity extraction failed: {e}")
        return empty_result


def count_total_entities(entities: dict[str, list[str]]) -> int:
    """Return the total count of all extracted entities."""
    return sum(len(v) for v in entities.values())
