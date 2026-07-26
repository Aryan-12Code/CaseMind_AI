"""
relationship_builder.py — Aggregates entity dossiers for the profile cards.
"""

from modules.database import get_all_processed_text, get_processed_by_evidence_id
from modules.entity_normalizer import clean_entity_name, is_valid_entity, resolve_duplicates

def build_entity_dossiers() -> list[dict]:
    """
    Builds a rich dossier for every Person identified in the case.
    """
    processed_files = get_all_processed_text()
    
    # Pass 1: Global Person Resolution
    all_persons_raw = []
    for file_record in processed_files:
        full = get_processed_by_evidence_id(file_record["evidence_id"])
        if full and full.get("entities", {}).get("persons"):
            for p in full["entities"]["persons"]:
                cleaned = clean_entity_name(p)
                if is_valid_entity(cleaned):
                    all_persons_raw.append(cleaned)
                    
    person_map = resolve_duplicates(all_persons_raw)
    
    # Initialize dossiers
    dossiers = {}
    
    # Pass 2: Aggregate data for each person
    for file_record in processed_files:
        evidence_id = file_record["evidence_id"]
        filename = file_record["filename"]
        
        full = get_processed_by_evidence_id(evidence_id)
        if not full:
            continue
            
        entities = full.get("entities", {})
        
        # Get valid entities for this file
        file_persons = set()
        if entities.get("persons"):
            for p in entities["persons"]:
                c = clean_entity_name(p)
                if is_valid_entity(c):
                    file_persons.add(person_map[c])
                    
        file_locs = set()
        if entities.get("locations"):
            for l in entities["locations"]:
                c = clean_entity_name(l)
                if is_valid_entity(c): file_locs.add(c)
                
        file_money = set()
        if entities.get("money"):
            for m in entities["money"]:
                c = clean_entity_name(m)
                if is_valid_entity(c): file_money.add(c)
                
        # For every person in this file, update their dossier
        for person in file_persons:
            if person not in dossiers:
                dossiers[person] = {
                    "name": person,
                    "role": "Unknown", # Placeholder for future role extraction
                    "connected_people": set(),
                    "locations": set(),
                    "documents": set(),
                    "money": set(),
                    "mentions": 0
                }
            
            d = dossiers[person]
            d["mentions"] += 1
            d["documents"].add(filename)
            
            # Add connections
            for other_person in file_persons:
                if other_person != person:
                    d["connected_people"].add(other_person)
                    
            for loc in file_locs:
                d["locations"].add(loc)
                
            for money in file_money:
                d["money"].add(money)

    # Convert sets to sorted lists for clean UI rendering
    final_list = []
    for person_name in sorted(dossiers.keys()):
        d = dossiers[person_name]
        final_list.append({
            "name": d["name"],
            "role": d["role"],
            "connected_people": sorted(list(d["connected_people"])),
            "locations": sorted(list(d["locations"])),
            "documents": sorted(list(d["documents"])),
            "money": sorted(list(d["money"])),
            "mentions": d["mentions"]
        })
        
    return final_list
