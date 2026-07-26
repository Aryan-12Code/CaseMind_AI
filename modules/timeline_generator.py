"""
timeline_generator.py — Chronological event extraction for CaseMind AI.

Scans processed evidence for dates and correlates them with file context
to build an interactive vertical timeline of events.

This module builds the Investigation Timeline from the actual evidence
(raw text, metadata, entities, keywords) — NOT from processing logs.
"""

import re
from datetime import datetime
from modules.database import get_all_processed_text, get_processed_by_evidence_id
from dateutil import parser as dateparser
from collections import defaultdict


# ── Regex helpers to extract structured data directly from raw text ──────────

_DATE_PATTERNS = [
    # 14 July 2026, 14-07-2026, 2026-07-14, etc.
    r'\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})\b',
    r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',
    r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
    r'\b(\d{4}[\-/]\d{1,2}[\-/]\d{1,2})\b',
]

_MONEY_PATTERNS = [
    r'(?:Rs\.?\s*|INR\s*|₹\s*)([\d,]+(?:\.\d{1,2})?)',
    r'([\d,]+(?:\.\d{1,2})?)\s*(?:rupees|rs)',
]

_TIME_PATTERN = r'\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm))?)\b'


def _extract_dates_from_text(text: str) -> list[str]:
    """Pull all recognizable date strings from raw text."""
    found = []
    for pattern in _DATE_PATTERNS:
        found.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(found))


def _extract_money_from_text(text: str) -> list[str]:
    """Pull monetary amounts from raw text."""
    found = []
    for pattern in _MONEY_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            found.append(f"Rs.{match}")
    return list(set(found))


def _extract_times_from_text(text: str) -> list[str]:
    """Pull time stamps from raw text."""
    return list(set(re.findall(_TIME_PATTERN, text)))


def _extract_persons_from_text(text: str) -> list[str]:
    """
    Supplement spaCy NER by scanning for chat-style 'Name:' patterns
    and common named references in the text.
    """
    # Chat format: "Rahul: some message"
    chat_names = re.findall(r'^([A-Z][a-z]+):', text, re.MULTILINE)
    # CCTV format: "19:48 Rahul entered"
    cctv_names = re.findall(r'\d{1,2}:\d{2}\s+([A-Z][a-z]+)\s+(?:entered|exited|arrived|left)', text)
    
    all_names = set(chat_names + cctv_names)
    # Filter out common false positives
    noise = {"From", "To", "Subject", "Date", "Row", "Columns", "Total",
             "Password", "Meeting", "Receipt", "Amount", "Item", "Quantity",
             "Owner", "Sender", "Receiver", "Remark", "Payment", "Customer",
             "Method", "Bank", "Transfer", "Office", "Cash", "Box", "Demo",
             "Warehouse", "Locker", "Evidence", "Statement", "Witness"}
    return sorted(all_names - noise)


def _extract_locations_from_text(text: str) -> list[str]:
    """Pull location references from raw text using keyword patterns."""
    locations = set()
    # Explicit "Warehouse X" references
    wh = re.findall(r'(Warehouse\s+[A-Z0-9](?:\b))', text)
    locations.update(wh)
    return sorted(locations)


def _infer_event(filename: str, filetype: str, raw_text: str,
                 metadata: dict, persons: list, locations: list,
                 money: list) -> tuple[str, str, list[str]]:
    """
    Infer (icon, title, bullet_points) for an evidence file based on
    its type, metadata and content.
    Returns a list of bullet-point strings for the description.
    """
    fn_lower = filename.lower()
    bullets = []

    # --- Email ---
    if filetype == "eml":
        sender = metadata.get("from", "Unknown")
        receiver = metadata.get("to", "Unknown")
        subject = metadata.get("subject", "")
        bullets.append(f"Email sent from {sender} to {receiver}.")
        if subject:
            bullets.append(f'Subject: "{subject}".')
        body_text = raw_text.split("--- Email Body ---")[-1].strip() if "--- Email Body ---" in raw_text else ""
        if body_text and len(body_text) < 200:
            bullets.append(f"Content: {body_text}")
        return "📧", "Email Communication", bullets

    # --- CCTV / Surveillance ---
    if "cctv" in fn_lower or "surveillance" in fn_lower:
        entries = re.findall(r'(\d{1,2}:\d{2})\s+(\w+)\s+(entered|exited|arrived|left)', raw_text)
        if entries:
            for time, name, action in entries:
                bullets.append(f"{name} {action} at {time}.")
            return "📹", "CCTV / Surveillance Log", bullets
        bullets.append("Movement activity captured on surveillance.")
        return "📹", "CCTV / Surveillance Log", bullets

    # --- Chat (exclude CSV files which match the Name: pattern) ---
    if filetype not in ("csv",) and ("chat" in fn_lower or re.search(r'^[A-Z][a-z]+:', raw_text, re.MULTILINE)):
        noise_names = {"From", "To", "Subject", "Date", "Columns", "Total",
                       "Row", "Password", "Amount", "Customer", "Item",
                       "Quantity", "Owner", "Sender", "Receiver", "Remark"}
        chat_lines = re.findall(r'^([A-Z][a-z]+):\s*(.+)', raw_text, re.MULTILINE)
        real_chat = [(n, m) for n, m in chat_lines if n not in noise_names]
        if real_chat:
            for name, msg in real_chat:
                bullets.append(f'{name}: "{msg.strip()[:80]}"')
            return "💬", "Chat / Messaging Activity", bullets

    # --- Financial ---
    if money or "receipt" in fn_lower or "bank" in fn_lower or "payment" in fn_lower:
        if persons:
            bullets.append(f"Parties involved: {', '.join(persons)}.")
        if money:
            for m in money:
                bullets.append(f"Amount: {m}.")
        # Try to extract row-level detail from CSVs
        rows = re.findall(r'Row \d+: (.+)', raw_text)
        if rows:
            for row in rows[:5]:
                bullets.append(row.strip())
        if not bullets:
            bullets.append("Financial record found.")
        return "💰", "Financial Transaction", bullets

    # --- Witness / Statement ---
    if "witness" in fn_lower or "statement" in fn_lower:
        # Extract key sentences
        sentences = [s.strip() for s in raw_text.replace('\n', ' ').split('.') if len(s.strip()) > 15]
        # Skip the header line
        for s in sentences:
            if not s.lower().startswith(('witness statement', '---')):
                bullets.append(s.strip() + '.')
        if not bullets:
            bullets.append("Witness statement recorded.")
        return "📋", "Witness Statement", bullets

    # --- Inventory ---
    if "inventory" in fn_lower:
        rows = re.findall(r'Row \d+: (.+)', raw_text)
        for row in rows:
            bullets.append(row.strip())
        if not bullets:
            bullets.append("Items and ownership documented.")
        return "📦", "Inventory Record", bullets

    # --- Password / credentials ---
    if "password" in fn_lower or "credential" in fn_lower:
        bullets.append("Authentication credentials found in evidence.")
        return "🔑", "Credential / Password Note", bullets

    # --- OCR / Image ---
    if filetype in ("png", "jpg", "jpeg"):
        ocr_lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        for line in ocr_lines:
            bullets.append(f"OCR: {line}")
        if not bullets:
            bullets.append("Text extracted from image via OCR.")
        return "🖼️", f"Image Evidence: {filename}", bullets

    # --- PDF ---
    if filetype == "pdf":
        if persons:
            bullets.append(f"References: {', '.join(persons[:4])}.")
        if locations:
            bullets.append(f"Locations: {', '.join(locations)}.")
        if not bullets:
            bullets.append("Document content extracted.")
        return "📄", f"Document: {filename}", bullets

    # --- CSV ---
    if filetype == "csv":
        bullets.append("Structured data from spreadsheet.")
        return "📊", f"Data Record: {filename}", bullets

    # --- Fallback ---
    if persons:
        bullets.append(f"Evidence mentioning {', '.join(persons)}.")
    else:
        bullets.append("Activity recorded in evidence file.")
    return "📎", f"Evidence: {filename}", bullets


def generate_timeline_events(sort_order: str = "Newest First",
                             include_system_logs: bool = False) -> list[dict]:
    """
    Generate chronological events extracted from evidence.

    Args:
        sort_order: 'Newest First' or 'Oldest First'.
        include_system_logs: If True, include internal application logs.

    Returns:
        List of dicts representing events.
    """
    processed_files = get_all_processed_text()
    events = []

    # Grouping structure for merging events that share the same date
    grouped = defaultdict(lambda: {
        "parsed_date": None,
        "sub_events": [],
        "all_persons": set(),
        "all_locations": set(),
        "all_money": set(),
        "all_sources": set(),
    })

    for file_record in processed_files:
        evidence_id = file_record["evidence_id"]
        filename = file_record["filename"]
        filetype = file_record["filetype"].lower()

        full = get_processed_by_evidence_id(evidence_id)
        if not full:
            continue

        raw_text = full.get("raw_text", "")
        metadata = full.get("metadata", {})
        entities = full.get("entities", {})
        keywords = full.get("keywords", {})

        # Skip the README / demo files
        if filename.lower() in ("readme.txt",):
            continue

        # ── 1. System logs (optional) ────────────────────────────────────
        if include_system_logs:
            ts = full.get("processed_time", "")
            if ts:
                try:
                    pd = dateparser.parse(ts, fuzzy=True)
                    events.append({
                        "date_str": ts,
                        "parsed_date": pd,
                        "title": f"System: Processed {filename}",
                        "desc": "File processed by CaseMind AI pipeline.",
                        "icon": "⚙️",
                        "source": filename,
                        "persons": "",
                        "locations": "",
                        "money": "",
                        "is_system_log": True,
                    })
                except Exception:
                    pass

        # ── 2. Gather ALL available data ─────────────────────────────────
        # Dates: combine entities + keywords + raw-text regex + metadata
        all_dates = set()
        all_dates.update(entities.get("dates", []))
        all_dates.update(keywords.get("dates", []))
        all_dates.update(_extract_dates_from_text(raw_text))
        meta_date = metadata.get("date", "")
        if meta_date and meta_date.strip():
            all_dates.add(meta_date.strip())
        # Remove bare years like "2026" that aren't useful timeline anchors
        all_dates = {d for d in all_dates if d and not re.fullmatch(r'\d{4}', d.strip())}

        # Locations: combine entities + raw-text regex (compute BEFORE persons to filter cross-contamination)
        locations = list(set(entities.get("locations", [])) | set(_extract_locations_from_text(raw_text)))

        # Persons: combine entities + raw-text regex
        persons = list(set(entities.get("persons", [])) | set(_extract_persons_from_text(raw_text)))
        # Remove known location names that spaCy misclassifies as persons
        persons = [p for p in persons if p not in locations and p.lower() not in
                   ("warehouse b", "warehouse a", "warehouse")]

        # Money: combine entities + raw-text regex
        money = list(set(entities.get("money", [])) | set(_extract_money_from_text(raw_text)))

        # ── 3. Infer the event ───────────────────────────────────────────
        icon, title, bullets = _infer_event(
            filename, filetype, raw_text, metadata, persons, locations, money
        )

        # ── 4. Group by date (or "Unknown Date") ────────────────────
        if not all_dates:
            all_dates = {"Unknown Date"}

        for date_str in all_dates:
            parsed = None
            group_key = date_str  # Default key is the raw string
            if date_str != "Unknown Date":
                try:
                    parsed = dateparser.parse(date_str, fuzzy=True, dayfirst=True)
                    if parsed and not (1900 < parsed.year < 2100):
                        continue
                    # Normalize to YYYY-MM-DD so "14 July 2026" and "14-07-2026" merge
                    group_key = parsed.strftime("%Y-%m-%d")
                except Exception:
                    continue

            g = grouped[group_key]
            if parsed:
                g["parsed_date"] = parsed
                # Keep the most human-readable date string
                if not g.get("display_date") or len(date_str) > len(g["display_date"]):
                    g["display_date"] = date_str
            g["sub_events"].append({"icon": icon, "title": title, "bullets": bullets})
            g["all_persons"].update(persons)
            g["all_locations"].update(locations)
            g["all_money"].update(money)
            g["all_sources"].add(filename)

    # ── 5. Compile merged events ─────────────────────────────────────────
    for group_key, g in grouped.items():
        subs = g["sub_events"]
        if len(subs) == 1:
            icon = subs[0]["icon"]
            title = subs[0]["title"]
        else:
            icon = "📌"
            title = f"Multiple Events ({len(subs)})"

        # Collect all bullets from all sub-events into one clean list
        all_bullets = []
        for s in subs:
            all_bullets.extend(s["bullets"])
        # Deduplicate while preserving order
        seen = set()
        unique_bullets = []
        for b in all_bullets:
            if b not in seen:
                seen.add(b)
                unique_bullets.append(b)
        # Build the HTML bullet list
        desc = '<div style="margin-top:6px"><b>Summary</b></div>'
        desc += '<ul style="margin:4px 0 0 16px;padding:0;list-style:disc">'
        for b in unique_bullets:
            desc += f'<li style="margin-bottom:3px">{b}</li>'
        desc += '</ul>'

        # Use the human-readable date, falling back to the group key
        display_date = g.get("display_date", group_key)

        events.append({
            "date_str": display_date,
            "parsed_date": g["parsed_date"] or datetime.min,
            "title": title,
            "desc": desc,
            "icon": icon,
            "source": ", ".join(sorted(g["all_sources"])),
            "persons": ", ".join(sorted(g["all_persons"])),
            "locations": ", ".join(sorted(g["all_locations"])),
            "money": ", ".join(sorted(g["all_money"])),
            "is_system_log": False,
        })

    # ── 6. Sort ──────────────────────────────────────────────────────────
    reverse_sort = sort_order == "Newest First"
    # Separate "Unknown Date" events so they always appear at the end
    known = [e for e in events if e["date_str"] != "Unknown Date"]
    unknown = [e for e in events if e["date_str"] == "Unknown Date"]
    known.sort(key=lambda e: e["parsed_date"], reverse=reverse_sort)
    events = known + unknown

    return events

