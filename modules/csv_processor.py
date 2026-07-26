"""
csv_processor.py — CSV text extraction for CaseMind AI.

Reads a CSV file using pandas and converts all rows/columns into
a single readable text block for downstream search and analysis.
"""

from typing import Tuple
import pandas as pd


def process_csv(filepath: str) -> Tuple[str, dict]:
    """
    Read a CSV file and convert it into readable text.

    Args:
        filepath: Absolute path to the CSV file.

    Returns:
        Tuple of (extracted_text, metadata_dict).
        metadata contains: row_count, column_count, columns (list of names).

    Raises:
        Exception: If the CSV cannot be parsed.
    """
    df = pd.read_csv(filepath, dtype=str)

    metadata = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
    }

    # Build a readable text representation
    lines = []
    lines.append(f"Columns: {', '.join(df.columns)}")
    lines.append(f"Total Rows: {len(df)}")
    lines.append("")

    for idx, row in df.iterrows():
        row_parts = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
        lines.append(f"Row {idx + 1}: {' | '.join(row_parts)}")

    combined_text = "\n".join(lines)
    return combined_text, metadata
