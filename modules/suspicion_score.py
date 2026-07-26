"""
suspicion_score.py — Rule-based suspicion scoring engine for CaseMind AI.

Analyzes processed evidence to assign a risk/suspicion score to detected persons.
"""

from modules.database import get_all_evidence, get_processed_by_evidence_id
from modules.entity_normalizer import resolve_duplicates


def generate_suspicion_scores() -> list[dict]:
    """
    Generate suspicion scores for all detected persons based on rule matching.

    Returns:
        List of dicts: {"name": str, "score": int, "percentage": int, 
                        "risk_level": str, "risk_color": str, "reasons": list[str]}
        Sorted by score (descending).
    """
    all_evidence = get_all_evidence()
    
    # Track data per person: {person_name: {"files": set(), "text_context": []}}
    person_data = {}
    
    for evidence in all_evidence:
        processed = get_processed_by_evidence_id(evidence["id"])
        if not processed or processed["processing_status"] != "Completed":
            continue
            
        entities = processed.get("entities", {})
        persons = entities.get("persons", [])
        raw_text = processed.get("raw_text", "").lower()
        
        for person in set(persons):  # Use set to avoid double counting per file
            if person not in person_data:
                person_data[person] = {"files": set(), "text_context": []}
            
            person_data[person]["files"].add(evidence["filename"])
            person_data[person]["text_context"].append(raw_text)

    # Resolve person variants globally to merge stats (e.g. "Rahul" and "Rahul Sharma")
    all_persons = list(person_data.keys())
    resolved_map = resolve_duplicates(all_persons)
    
    merged_person_data = {}
    for raw_name, data in person_data.items():
        canonical_name = resolved_map.get(raw_name, raw_name)
        if canonical_name not in merged_person_data:
            merged_person_data[canonical_name] = {"files": set(), "text_context": []}
        
        merged_person_data[canonical_name]["files"].update(data["files"])
        merged_person_data[canonical_name]["text_context"].extend(data["text_context"])
        
    person_data = merged_person_data

    # Calculate scores
    results = []
    
    # Scoring Rules
    RULES = [
        {"keywords": ["money", "transfer", "paid", "payment", "$", "usd"], "points": 15, "reason": "Money Mention"},
        {"keywords": ["password", "login", "credential", "secret"], "points": 15, "reason": "Password/Secret Mention"},
        {"keywords": ["delete", "destroy", "shred", "hide", "wipe"], "points": 20, "reason": "Destruction of Evidence"},
        {"keywords": ["confidential", "classified", "do not share"], "points": 10, "reason": "Confidentiality Marker"},
        {"keywords": ["urgent", "asap", "immediately"], "points": 5, "reason": "Urgency Indicator"}
    ]

    for person, data in person_data.items():
        score = 0
        reasons = []
        
        # Rule 1: Appears in Multiple Files
        num_files = len(data["files"])
        if num_files > 1:
            score += 10
            reasons.append(f"Appears in {num_files} files (+10)")
            
        # Rule 2: Keyword Matching in associated text
        combined_text = " ".join(data["text_context"])
        
        for rule in RULES:
            for kw in rule["keywords"]:
                if kw in combined_text:
                    score += rule["points"]
                    reasons.append(f"{rule['reason']} (+{rule['points']})")
                    break # Score once per rule per person
                    
        # Cap score at 100
        percentage = min(score, 100)
        
        # Determine Risk Level
        if percentage >= 75:
            risk_level = "Critical"
            risk_color = "#F44336" # Red
        elif percentage >= 50:
            risk_level = "High"
            risk_color = "#FF9800" # Orange
        elif percentage >= 25:
            risk_level = "Medium"
            risk_color = "#FFC107" # Yellow
        else:
            risk_level = "Low"
            risk_color = "#4CAF50" # Green
            
        results.append({
            "name": person,
            "score": score,
            "percentage": percentage,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "reasons": reasons
        })
        
    # Sort descending by score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
