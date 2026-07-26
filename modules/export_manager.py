"""
export_manager.py — Data export utility for CaseMind AI.

Handles generating CSV, Excel, and JSON exports of the Case data.
"""

import json
import pandas as pd
import io
from modules.database import get_all_evidence, get_processed_by_evidence_id, get_dashboard_metrics
from modules.suspicion_score import generate_suspicion_scores


def get_case_data_dict() -> dict:
    """Gather all case data into a structured dictionary."""
    evidence = get_all_evidence()
    metrics = get_dashboard_metrics()
    suspects = generate_suspicion_scores()
    
    full_data = {
        "metrics": metrics,
        "evidence": evidence,
        "processed_evidence": [],
        "suspicion_scores": suspects
    }
    
    for ev in evidence:
        processed = get_processed_by_evidence_id(ev["id"])
        if processed:
            # Remove raw JSON string fields — the parsed dicts are already present
            clean = {k: v for k, v in processed.items()
                     if k not in ("metadata_json", "keywords_json", "entities_json")}
            full_data["processed_evidence"].append(clean)
            
    return full_data


def generate_export_json() -> bytes:
    """Generate a full JSON export of the case."""
    data = get_case_data_dict()
    return json.dumps(data, indent=2).encode('utf-8')


def generate_export_csv() -> bytes:
    """Generate a CSV export of just the evidence list."""
    evidence = get_all_evidence()
    df = pd.DataFrame(evidence)
    return df.to_csv(index=False).encode('utf-8')


def generate_export_excel() -> bytes:
    """Generate a multi-sheet Excel export (Evidence + Analytics)."""
    data = get_case_data_dict()
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Evidence
        if data["evidence"]:
            df_ev = pd.DataFrame(data["evidence"])
            df_ev.to_excel(writer, sheet_name="Evidence", index=False)
            
        # Sheet 2: Suspicion Scores
        if data["suspicion_scores"]:
            sus_list = []
            for s in data["suspicion_scores"]:
                sus_list.append({
                    "Name": s["name"],
                    "Risk Level": s["risk_level"],
                    "Score %": s["percentage"],
                    "Top Reason": s["reasons"][0] if s["reasons"] else ""
                })
            df_sus = pd.DataFrame(sus_list)
            df_sus.to_excel(writer, sheet_name="Suspicion Scores", index=False)
            
        # Sheet 3: Extracted Entities
        entities_list = []
        for p in data["processed_evidence"]:
            ents = p.get("entities", {})
            for cat, items in ents.items():
                for item in items:
                    entities_list.append({
                        "Source File": p["filename"],
                        "Category": cat.title(),
                        "Entity": item
                    })
        if entities_list:
            df_ent = pd.DataFrame(entities_list)
            df_ent.to_excel(writer, sheet_name="Extracted Entities", index=False)
            
    return output.getvalue()
