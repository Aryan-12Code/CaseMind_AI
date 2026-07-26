"""
ai_engine.py — Core Groq API wrapper for CaseMind AI.

Provides functions to initialize the Groq model, query evidence,
and generate case summaries. All responses are constrained to use
ONLY the provided evidence context.
"""

import json
from typing import Optional
import streamlit as st
import groq


def _format_api_error(e: Exception, context: str) -> str:
    """Format API errors into user-friendly messages."""
    error_str = str(e)
    if "429" in error_str or "RateLimitError" in error_str or isinstance(e, groq.RateLimitError):
        return (
            f"❌ {context}: API Rate Limit Exceeded.\n\n"
            "The provided API key has exhausted its current quota or free-tier limits. "
            "Please wait a moment before trying again, or upgrade your Groq billing plan."
        )
    return f"❌ {context}: {error_str}"


# ── System prompts ───────────────────────────────────────────────────────────

INVESTIGATION_SYSTEM_PROMPT = """You are CaseMind AI, a professional digital evidence investigation assistant.

CRITICAL RULES:
1. You must answer ONLY based on the evidence provided below. NEVER use general knowledge.
2. If the evidence does not contain information to answer the question, say "No relevant information found in the uploaded evidence."
3. Every answer MUST include the source filename where you found the information.
4. If possible, quote the exact text from the evidence that supports your answer.

FORMAT YOUR RESPONSE EXACTLY AS:
**Answer:** [Your detailed answer here]

**Source:** [filename(s) where information was found]

**Supporting Evidence:** [Exact quote or relevant excerpt from the evidence]
"""

SUMMARY_SYSTEM_PROMPT = """You are CaseMind AI, a professional digital evidence investigation assistant.

Analyze ALL the evidence provided below and generate a comprehensive investigation summary.

CRITICAL: Base your analysis ONLY on the provided evidence. Do NOT speculate or use general knowledge.

Generate your response in the following JSON format (and ONLY this JSON, no other text, do not use markdown code blocks):
{
    "case_summary": "Overall narrative summary of the case based on all evidence",
    "important_findings": ["Finding 1", "Finding 2"],
    "people_mentioned": ["Person 1", "Person 2"],
    "organizations": ["Org 1", "Org 2"],
    "locations": ["Location 1", "Location 2"],
    "important_dates": ["Date 1 - context", "Date 2 - context"],
    "monetary_transactions": ["Transaction 1", "Transaction 2"],
    "suspicious_keywords": ["Keyword 1", "Keyword 2"],
    "observations": ["Observation 1", "Observation 2"],
    "suggested_questions": [
        "Question about the evidence 1",
        "Question about the evidence 2"
    ]
}
"""

INSIGHTS_SYSTEM_PROMPT = """You are CaseMind AI. Analyze the evidence and return ONLY a JSON object (and ONLY JSON, no markdown code blocks) with these fields:

{
    "most_mentioned_person": {"name": "...", "count_approx": 0, "context": "..."},
    "most_important_date": {"date": "...", "context": "..."},
    "most_important_location": {"location": "...", "context": "..."},
    "most_frequent_keyword": {"keyword": "...", "context": "..."},
    "suspicious_activity": {"description": "...", "severity": "Low/Medium/High"}
}

Base this ONLY on the provided evidence. If a field cannot be determined, use "Not found" for string values and 0 for numbers.
"""

GROQ_MODEL = "llama-3.3-70b-versatile"


def test_connection(api_key: str) -> tuple[bool, str]:
    """
    Test the Groq API connection with a simple query.

    Returns:
        Tuple of (success: bool, message: str).
    """
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Respond with exactly: CONNECTION_OK"}],
            model=GROQ_MODEL
        )
        if response and response.choices and response.choices[0].message.content:
            return True, "✅ Connection successful! Groq API is ready."
        return False, "⚠️ Received empty response from Groq."
    except Exception as e:
        return False, f"❌ Connection failed: {e}"


def query_evidence(api_key: str, question: str, evidence_context: str) -> str:
    """
    Send a question to Groq with evidence as context.

    Args:
        api_key: Groq API key.
        question: The user's question.
        evidence_context: Formatted evidence text with source filenames.

    Returns:
        The AI's response text.
    """
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        full_prompt = (
            f"{INVESTIGATION_SYSTEM_PROMPT}\n\n"
            f"=== EVIDENCE START ===\n{evidence_context}\n=== EVIDENCE END ===\n\n"
            f"User Question: {question}"
        )

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=GROQ_MODEL
        )

        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        return "No response generated. Please try again."

    except Exception as e:
        return _format_api_error(e, "AI Query Error")


def generate_case_summary(api_key: str, evidence_context: str) -> Optional[dict]:
    """
    Generate a comprehensive case summary from all evidence.

    Args:
        api_key: Groq API key.
        evidence_context: Formatted evidence text.

    Returns:
        Parsed dictionary with summary fields, or None on failure.
    """
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        full_prompt = (
            f"{SUMMARY_SYSTEM_PROMPT}\n\n"
            f"=== EVIDENCE START ===\n{evidence_context}\n=== EVIDENCE END ==="
        )

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=GROQ_MODEL,
            response_format={"type": "json_object"}
        )

        if response and response.choices and response.choices[0].message.content:
            return _parse_json_response(response.choices[0].message.content)
        return None

    except Exception as e:
        st.error(_format_api_error(e, "Summary generation failed"))
        return None


def generate_insights(api_key: str, evidence_context: str) -> Optional[dict]:
    """
    Generate automatic investigation insights.

    Returns:
        Parsed dictionary with insight fields, or None on failure.
    """
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        full_prompt = (
            f"{INSIGHTS_SYSTEM_PROMPT}\n\n"
            f"=== EVIDENCE START ===\n{evidence_context}\n=== EVIDENCE END ==="
        )

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=GROQ_MODEL,
            response_format={"type": "json_object"}
        )

        if response and response.choices and response.choices[0].message.content:
            return _parse_json_response(response.choices[0].message.content)
        return None

    except Exception as e:
        st.error(_format_api_error(e, "Insight generation failed"))
        return None


def _parse_json_response(text: str) -> Optional[dict]:
    """
    Parse a JSON response from Groq, handling markdown code fences.
    """
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
    return None
