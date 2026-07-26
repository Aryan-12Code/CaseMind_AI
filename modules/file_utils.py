"""
file_utils.py — File handling utilities for CaseMind AI.

Handles saving uploaded files to categorized subfolders,
auto-renaming duplicates, and formatting file sizes for display.
"""

import os
import shutil
import streamlit as st
from typing import Tuple

# Base upload directory (relative to project root)
UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "cases")

# Mapping from file extension to subfolder name
EXTENSION_TO_FOLDER: dict[str, str] = {
    "pdf": "pdf",
    "png": "images",
    "jpg": "images",
    "jpeg": "images",
    "txt": "text",
    "csv": "csv",
    "eml": "email",
}

# Allowed extensions (used for validation)
ALLOWED_EXTENSIONS: set[str] = set(EXTENSION_TO_FOLDER.keys())


def get_file_extension(filename: str) -> str:
    """Extract the lowercase file extension from a filename (without the dot)."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_supported_file(filename: str) -> bool:
    """Check whether the file extension is in the supported list."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def _get_target_folder(extension: str) -> str:
    """Return the full path to the target subfolder scoped to the active case."""
    case_id = st.session_state.get("active_case_id")
    if not case_id:
        raise ValueError("No active case found in session state.")
        
    folder_name = EXTENSION_TO_FOLDER.get(extension, "other")
    target = os.path.join(UPLOAD_BASE, str(case_id), folder_name)
    os.makedirs(target, exist_ok=True)
    return target


def _resolve_duplicate(folder: str, filename: str) -> str:
    """
    If a file with the same name already exists in the folder,
    append (1), (2), etc. until a unique name is found.

    Example: chat.txt -> chat(1).txt -> chat(2).txt
    """
    base, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{base}({counter}){ext}"
        counter += 1
    return candidate


def save_uploaded_file(uploaded_file) -> Tuple[str, str, str, int, bool]:
    """
    Save an uploaded Streamlit file object to the correct subfolder.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        Tuple of (final_filename, filepath, filetype, filesize, was_renamed).
    """
    original_name: str = uploaded_file.name
    extension = get_file_extension(original_name)
    target_folder = _get_target_folder(extension)

    # Handle duplicate filenames
    final_name = _resolve_duplicate(target_folder, original_name)
    was_renamed = final_name != original_name

    filepath = os.path.join(target_folder, final_name)

    # Write file to disk
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    filesize = os.path.getsize(filepath)

    return final_name, filepath, extension, filesize, was_renamed


def delete_file(filepath: str) -> bool:
    """
    Delete a physical file from disk.

    Returns:
        True if the file was deleted, False if it didn't exist.
    """
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            pass
    return False


def delete_case_files(case_id: int) -> bool:
    """Delete the entire physical uploads directory for a case."""
    target_dir = os.path.join(UPLOAD_BASE, str(case_id))
    if os.path.exists(target_dir):
        try:
            shutil.rmtree(target_dir)
            return True
        except Exception:
            pass
    return False


def format_filesize(size_bytes: int) -> str:
    """
    Convert a file size in bytes to a human-readable string.

    Examples:
        1024       -> '1.00 KB'
        1048576    -> '1.00 MB'
        1073741824 -> '1.00 GB'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
