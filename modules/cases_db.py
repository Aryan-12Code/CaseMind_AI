"""
cases_db.py — Master database for Case Management.

Tracks the high-level list of cases. Each case will have its own
isolated database for evidence (`database/cases/<id>/evidence.db`).
"""

import sqlite3
import os
from datetime import datetime

# Master DB path
MASTER_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
MASTER_DB_PATH = os.path.join(MASTER_DB_DIR, "cases.db")


def _get_connection() -> sqlite3.Connection:
    """Get connection to the master cases database."""
    os.makedirs(MASTER_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_master_db() -> None:
    """Initialize the Cases table if it doesn't exist."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'In Progress',
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_case(name: str) -> int:
    """Create a new case and return its ID."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Cases (name, created_at, updated_at)
        VALUES (?, ?, ?)
    """, (name, now, now))
    conn.commit()
    case_id = cursor.lastrowid
    conn.close()
    return case_id


def get_all_cases() -> list[dict]:
    """Retrieve all cases, ordered by most recently updated."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cases ORDER BY updated_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def rename_case(case_id: int, new_name: str) -> None:
    """Rename an existing case."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Cases SET name = ?, updated_at = ? WHERE id = ?", (new_name, now, case_id))
    conn.commit()
    conn.close()


def update_case_status(case_id: int, status: str) -> None:
    """Update case status (In Progress, Completed, Archived)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Cases SET status = ?, updated_at = ? WHERE id = ?", (status, now, case_id))
    conn.commit()
    conn.close()


def delete_case(case_id: int) -> None:
    """Delete a case from the master DB."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cases WHERE id = ?", (case_id,))
    conn.commit()
    conn.close()


def get_case_by_id(case_id: int) -> dict | None:
    """Get details for a single case."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
