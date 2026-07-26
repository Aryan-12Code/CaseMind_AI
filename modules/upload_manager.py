"""
upload_manager.py — Evidence Manager UI component for CaseMind AI.

Displays the evidence table with search, filter, sort, preview,
extracted text view, download, and delete capabilities.
"""

import os
import streamlit as st
from typing import Optional
from modules.database import (
    get_all_evidence, get_evidence_by_id, delete_evidence,
    get_processed_by_evidence_id,
)
from modules.file_utils import format_filesize, delete_file
from modules.file_preview import render_preview


# ── Icon mapping for file types ──────────────────────────────────────────────
FILE_ICONS: dict[str, str] = {
    "pdf": "📄",
    "txt": "📝",
    "csv": "📊",
    "png": "🖼️",
    "jpg": "🖼️",
    "jpeg": "🖼️",
    "eml": "📧",
}

# ── Processing status styling ────────────────────────────────────────────────
STATUS_STYLES: dict[str, tuple[str, str]] = {
    "Completed": ("#4CAF50", "✅"),
    "Failed": ("#FF5722", "❌"),
    "Processing": ("#FFC107", "⏳"),
    "Waiting": ("#888", "⏳"),
    "Uploaded": ("#2196F3", "📤"),
}


def render_evidence_manager() -> None:
    """Render the full Evidence Manager section: search, filters, table, and actions."""
    st.markdown("---")
    st.subheader("📁 Evidence Manager")

    all_evidence = get_all_evidence()

    if not all_evidence:
        st.info("No evidence uploaded yet. Use the uploader above to get started.")
        return

    # ── Search, Filter, Sort controls ────────────────────────────────────────
    col_search, col_filter, col_sort = st.columns([3, 2, 2])

    with col_search:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by filename, type, or date...",
            label_visibility="collapsed",
            key="evidence_mgr_search",
        )

    with col_filter:
        filter_type = st.selectbox(
            "Filter by type",
            ["All", "PDF", "Images", "TXT", "CSV", "EML"],
            label_visibility="collapsed",
            key="evidence_mgr_filter",
        )

    with col_sort:
        sort_option = st.selectbox(
            "Sort by",
            ["Newest", "Oldest", "Largest", "Smallest", "Alphabetical"],
            label_visibility="collapsed",
            key="evidence_mgr_sort",
        )

    # ── Apply filters ────────────────────────────────────────────────────────
    filtered = _apply_filters(all_evidence, search_query, filter_type)
    filtered = _apply_sort(filtered, sort_option)

    if not filtered:
        st.warning("No evidence matches your search or filter criteria.")
        return

    st.caption(f"Showing {len(filtered)} of {len(all_evidence)} evidence files")

    # ── Render evidence table ────────────────────────────────────────────────
    for evidence in filtered:
        _render_evidence_row(evidence)


def _apply_filters(evidence_list: list[dict], search: str, type_filter: str) -> list[dict]:
    """Filter the evidence list by search query and type filter."""
    results = evidence_list

    if type_filter != "All":
        type_map = {
            "PDF": ["pdf"],
            "Images": ["png", "jpg", "jpeg"],
            "TXT": ["txt"],
            "CSV": ["csv"],
            "EML": ["eml"],
        }
        allowed_types = type_map.get(type_filter, [])
        results = [e for e in results if e["filetype"] in allowed_types]

    if search:
        query = search.lower()
        results = [
            e for e in results
            if query in e["filename"].lower()
            or query in e["filetype"].lower()
            or query in e["upload_time"].lower()
        ]

    return results


def _apply_sort(evidence_list: list[dict], sort_option: str) -> list[dict]:
    """Sort the evidence list based on the selected sort option."""
    if sort_option == "Newest":
        return sorted(evidence_list, key=lambda e: e["id"], reverse=True)
    elif sort_option == "Oldest":
        return sorted(evidence_list, key=lambda e: e["id"])
    elif sort_option == "Largest":
        return sorted(evidence_list, key=lambda e: e["filesize"], reverse=True)
    elif sort_option == "Smallest":
        return sorted(evidence_list, key=lambda e: e["filesize"])
    elif sort_option == "Alphabetical":
        return sorted(evidence_list, key=lambda e: e["filename"].lower())
    return evidence_list


def _render_evidence_row(evidence: dict) -> None:
    """Render a single evidence item as a styled row with actions."""
    icon = FILE_ICONS.get(evidence["filetype"], "📎")
    size_str = format_filesize(evidence["filesize"])
    eid = evidence["id"]

    # Check processing status
    processed = get_processed_by_evidence_id(eid)
    proc_status = processed["processing_status"] if processed else "Waiting"
    status_color, status_icon = STATUS_STYLES.get(proc_status, ("#888", "⏳"))

    # Row container
    with st.container():
        col_icon, col_name, col_type, col_size, col_time, col_status, col_actions = st.columns(
            [0.5, 2.5, 0.8, 0.8, 1.2, 1, 3.2]
        )

        with col_icon:
            st.markdown(f"<div style='font-size:1.5em; padding-top:8px;'>{icon}</div>",
                        unsafe_allow_html=True)
        with col_name:
            st.markdown(f"**{evidence['filename']}**")
        with col_type:
            st.caption(evidence["filetype"].upper())
        with col_size:
            st.caption(size_str)
        with col_time:
            st.caption(evidence["upload_time"])
        with col_status:
            st.markdown(
                f"<span style='color:{status_color}; font-size:0.85em;'>"
                f"{status_icon} {proc_status}</span>",
                unsafe_allow_html=True,
            )
        with col_actions:
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            with btn_col1:
                if st.button("👁", key=f"view_{eid}", use_container_width=True,
                             help="Preview file"):
                    st.session_state[f"preview_{eid}"] = not st.session_state.get(f"preview_{eid}", False)
            with btn_col2:
                if st.button("📝", key=f"text_{eid}", use_container_width=True,
                             help="View extracted text"):
                    st.session_state[f"extracted_{eid}"] = not st.session_state.get(f"extracted_{eid}", False)
            with btn_col3:
                filepath = evidence["filepath"]
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        st.download_button(
                            "⬇", data=f.read(),
                            file_name=evidence["filename"],
                            key=f"dl_{eid}",
                            use_container_width=True,
                            help="Download file",
                        )
                else:
                    st.button("⬇", key=f"dl_{eid}", disabled=True, use_container_width=True)
            with btn_col4:
                if st.button("🗑", key=f"del_{eid}", use_container_width=True,
                             help="Delete evidence"):
                    st.session_state[f"confirm_delete_{eid}"] = True

    # ── Delete confirmation ──────────────────────────────────────────────────
    if st.session_state.get(f"confirm_delete_{eid}", False):
        st.warning(f"⚠️ Are you sure you want to delete **{evidence['filename']}**? This cannot be undone.")
        c1, c2, _ = st.columns([1, 1, 5])
        with c1:
            if st.button("✅ Yes, Delete", key=f"confirm_yes_{eid}", type="primary"):
                delete_file(evidence["filepath"])
                delete_evidence(eid)
                st.session_state[f"confirm_delete_{eid}"] = False
                st.success(f"✓ **{evidence['filename']}** deleted successfully.")
                st.rerun()
        with c2:
            if st.button("❌ Cancel", key=f"confirm_no_{eid}"):
                st.session_state[f"confirm_delete_{eid}"] = False
                st.rerun()

    # ── File preview expander ────────────────────────────────────────────────
    if st.session_state.get(f"preview_{eid}", False):
        with st.expander(f"Preview — {evidence['filename']}", expanded=True):
            render_preview(evidence["filepath"], evidence["filetype"])

    # ── Extracted text expander ──────────────────────────────────────────────
    if st.session_state.get(f"extracted_{eid}", False):
        with st.expander(f"📝 Extracted Text — {evidence['filename']}", expanded=True):
            if processed and processed.get("raw_text"):
                text = processed["raw_text"]
                st.caption(f"{len(text):,} characters extracted | Status: {proc_status}")
                st.code(text[:20_000], language="text")
                if len(text) > 20_000:
                    st.caption("ℹ️ Showing first 20,000 characters.")

                # Link to full details
                if st.button(f"🔍 View Full Details", key=f"details_btn_{eid}"):
                    st.session_state["view_details_id"] = eid
                    st.rerun()
            elif processed and processed["processing_status"] == "Failed":
                st.error(f"Processing failed: {processed.get('error_message', 'Unknown error')}")
            else:
                st.info("No extracted text available.")

    # Subtle divider
    st.markdown("<hr style='margin:5px 0; border-color:#333;'/>", unsafe_allow_html=True)
