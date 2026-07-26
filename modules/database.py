"""
database.py — SQLite database module for CaseMind AI.

Manages the Evidence and ProcessedEvidence tables.
All functions use a shared connection path to `database/evidence.db`.
"""

import sqlite3
import json
import os
import streamlit as st
from typing import Optional

# Base directory for case databases
DB_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "cases")


def _get_connection() -> sqlite3.Connection:
    """Create and return a database connection scoped to the active case."""
    case_id = st.session_state.get("active_case_id")
    if not case_id:
        raise ValueError("No active case found in session state. Cannot connect to scoped database.")
        
    case_dir = os.path.join(DB_BASE_DIR, str(case_id))
    os.makedirs(case_dir, exist_ok=True)
    
    db_path = os.path.join(case_dir, "evidence.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database and create all tables if they don't exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    # Original Evidence table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Evidence (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT    NOT NULL,
            filepath    TEXT    NOT NULL,
            filetype    TEXT    NOT NULL,
            filesize    INTEGER NOT NULL,
            upload_time TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Uploaded'
        )
    """)

    # ProcessedEvidence table (Phase 3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProcessedEvidence (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id         INTEGER NOT NULL,
            filename            TEXT    NOT NULL,
            filetype            TEXT    NOT NULL,
            raw_text            TEXT    DEFAULT '',
            metadata_json       TEXT    DEFAULT '{}',
            keywords_json       TEXT    DEFAULT '{}',
            entities_json       TEXT    DEFAULT '{}',
            processed_time      TEXT    NOT NULL,
            processing_status   TEXT    NOT NULL DEFAULT 'Waiting',
            error_message       TEXT,
            FOREIGN KEY (evidence_id) REFERENCES Evidence(id) ON DELETE CASCADE
        )
    """)

    # ConversationHistory table (Phase 4)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ConversationHistory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question    TEXT    NOT NULL,
            answer      TEXT    NOT NULL,
            sources     TEXT    DEFAULT '',
            confidence  TEXT    DEFAULT '',
            timestamp   TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ── Evidence CRUD ────────────────────────────────────────────────────────────

def add_evidence(filename: str, filepath: str, filetype: str,
                 filesize: int, upload_time: str, status: str = "Uploaded") -> int:
    """
    Insert a new evidence record into the database.

    Returns:
        The row id of the newly inserted record.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Evidence (filename, filepath, filetype, filesize, upload_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, filepath, filetype, filesize, upload_time, status))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_evidence() -> list[dict]:
    """
    Retrieve all evidence records from the database.

    Returns:
        A list of dictionaries, each representing an evidence record.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evidence ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def delete_evidence(evidence_id: int) -> bool:
    """
    Delete an evidence record and its associated processed data by id.

    Returns:
        True if a record was deleted, False otherwise.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    # Delete processed data first
    cursor.execute("DELETE FROM ProcessedEvidence WHERE evidence_id = ?", (evidence_id,))
    cursor.execute("DELETE FROM Evidence WHERE id = ?", (evidence_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_evidence_by_id(evidence_id: int) -> Optional[dict]:
    """Retrieve a single evidence record by its id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evidence WHERE id = ?", (evidence_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_evidence_status(evidence_id: int, status: str) -> None:
    """Update the status field of an evidence record."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Evidence SET status = ? WHERE id = ?", (status, evidence_id))
    conn.commit()
    conn.close()


# ── ProcessedEvidence CRUD ───────────────────────────────────────────────────

def add_processed_evidence(
    evidence_id: int,
    filename: str,
    filetype: str,
    raw_text: str,
    metadata: dict,
    keywords: dict,
    entities: dict,
    processed_time: str,
    processing_status: str = "Completed",
    error_message: Optional[str] = None,
) -> int:
    """
    Insert a new processed evidence record.

    Returns:
        The row id of the newly inserted record.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ProcessedEvidence
            (evidence_id, filename, filetype, raw_text, metadata_json,
             keywords_json, entities_json, processed_time, processing_status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evidence_id, filename, filetype, raw_text,
        json.dumps(metadata), json.dumps(keywords), json.dumps(entities),
        processed_time, processing_status, error_message
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_processed_by_evidence_id(evidence_id: int) -> Optional[dict]:
    """
    Retrieve the processed data for a given evidence_id.

    Returns:
        Dictionary with parsed JSON fields, or None if not found.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ProcessedEvidence WHERE evidence_id = ?", (evidence_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    result = dict(row)
    # Parse JSON fields
    result["metadata"] = json.loads(result.get("metadata_json", "{}"))
    result["keywords"] = json.loads(result.get("keywords_json", "{}"))
    result["entities"] = json.loads(result.get("entities_json", "{}"))
    return result


def delete_processed_evidence(evidence_id: int) -> bool:
    """Delete processed data for a given evidence_id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ProcessedEvidence WHERE evidence_id = ?", (evidence_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def search_processed_text(query: str) -> list[dict]:
    """
    Search across all processed evidence text for a keyword (case-insensitive).

    Returns:
        List of dicts with evidence_id, filename, filetype, raw_text.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT evidence_id, filename, filetype, raw_text
        FROM ProcessedEvidence
        WHERE raw_text LIKE ? AND processing_status = 'Completed'
    """, (f"%{query}%",))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ── Dashboard Metrics ────────────────────────────────────────────────────────

def get_dashboard_metrics() -> dict:
    """
    Compute dashboard metrics from Evidence and ProcessedEvidence tables.

    Returns:
        Dictionary with keys: total_evidence, total_pdfs, total_images,
        storage_used_bytes, processed_files, pending_files,
        total_text_chars, total_entities.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    # Evidence metrics
    cursor.execute("SELECT COUNT(*) FROM Evidence")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Evidence WHERE filetype = 'pdf'")
    total_pdfs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Evidence WHERE filetype IN ('png', 'jpg', 'jpeg')")
    total_images = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(filesize), 0) FROM Evidence")
    storage_bytes = cursor.fetchone()[0]

    # Processing metrics
    cursor.execute("SELECT COUNT(*) FROM ProcessedEvidence WHERE processing_status = 'Completed'")
    processed = cursor.fetchone()[0]

    pending = total - processed  # Files uploaded but not yet processed (or failed)

    cursor.execute("SELECT COALESCE(SUM(LENGTH(raw_text)), 0) FROM ProcessedEvidence WHERE processing_status = 'Completed'")
    total_text_chars = cursor.fetchone()[0]

    # Count total entities by summing entity list lengths from JSON
    cursor.execute("SELECT entities_json FROM ProcessedEvidence WHERE processing_status = 'Completed'")
    entity_rows = cursor.fetchall()
    total_entities = 0
    for row in entity_rows:
        try:
            entities = json.loads(row[0])
            total_entities += sum(len(v) for v in entities.values())
        except (json.JSONDecodeError, TypeError):
            pass

    conn.close()
    return {
        "total_evidence": total,
        "total_pdfs": total_pdfs,
        "total_images": total_images,
        "storage_used_bytes": storage_bytes,
        "processed_files": processed,
        "pending_files": max(0, pending),
        "total_text_chars": total_text_chars,
        "total_entities": total_entities,
    }


# ── Conversation History CRUD ────────────────────────────────────────────────

def add_conversation(question: str, answer: str, sources: str,
                     confidence: str, timestamp: str) -> int:
    """Insert a conversation record. Returns the row id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ConversationHistory (question, answer, sources, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (question, answer, sources, confidence, timestamp))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_conversations() -> list[dict]:
    """Retrieve all conversations, newest first."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ConversationHistory ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def clear_conversations() -> None:
    """Delete all conversation history."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ConversationHistory")
    conn.commit()
    conn.close()


# ── Evidence Context Helper ──────────────────────────────────────────────────

def get_all_processed_text() -> list[dict]:
    """
    Get all successfully processed evidence with their text.

    Returns:
        List of dicts with: evidence_id, filename, filetype, raw_text.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT evidence_id, filename, filetype, raw_text
        FROM ProcessedEvidence
        WHERE processing_status = 'Completed' AND raw_text != ''
        ORDER BY evidence_id
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
