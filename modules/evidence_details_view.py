"""
evidence_details_view.py — Evidence Details page for CaseMind AI.

Displays comprehensive details for a single piece of evidence:
  - File information
  - Processing metadata
  - Extracted text
  - Keywords (regex-detected)
  - Named entities (spaCy NER)
"""

import streamlit as st
from modules.database import get_evidence_by_id, get_processed_by_evidence_id
from modules.file_utils import format_filesize


# ── Category display config ──────────────────────────────────────────────────
KEYWORD_ICONS = {
    "emails": "📧",
    "phone_numbers": "📞",
    "dates": "📅",
    "currency": "💰",
    "urls": "🔗",
    "numbers": "🔢",
}

ENTITY_ICONS = {
    "persons": "👤",
    "organizations": "🏢",
    "locations": "📍",
    "dates": "📅",
    "money": "💵",
}


def render(evidence_id: int) -> None:
    """Render the full Evidence Details page for a given evidence_id."""

    evidence = get_evidence_by_id(evidence_id)
    if not evidence:
        st.error("Evidence not found.")
        return

    processed = get_processed_by_evidence_id(evidence_id)

    # ── Header ───────────────────────────────────────────────────────────────
    st.title(f"🔍 Evidence Details")

    # Back button
    if st.button("← Back to Evidence Manager"):
        st.session_state.pop("view_details_id", None)
        st.rerun()

    st.markdown("---")

    # ── File Information Card ────────────────────────────────────────────────
    st.subheader("📋 File Information")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Filename", evidence["filename"])
    with col2:
        st.metric("Type", evidence["filetype"].upper())
    with col3:
        st.metric("Size", format_filesize(evidence["filesize"]))
    with col4:
        st.metric("Uploaded", evidence["upload_time"])

    st.markdown("---")

    if not processed:
        st.warning("⏳ This file has not been processed yet.")
        return

    # ── Processing Metadata ──────────────────────────────────────────────────
    st.subheader("⚙️ Processing Information")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        status = processed["processing_status"]
        color = "#4CAF50" if status == "Completed" else "#FF5722" if status == "Failed" else "#FFC107"
        st.markdown(f"**Status:** <span style='color:{color};'>{status}</span>", unsafe_allow_html=True)
    with meta_col2:
        st.markdown(f"**Processed At:** {processed['processed_time']}")
    with meta_col3:
        # Display file-type specific metadata
        metadata = processed.get("metadata", {})
        if metadata:
            meta_items = [f"{k}: {v}" for k, v in metadata.items() if v is not None]
            st.markdown(f"**Metadata:** {' | '.join(meta_items) if meta_items else 'N/A'}")

    if processed.get("error_message"):
        st.error(f"❌ Error: {processed['error_message']}")

    st.markdown("---")

    # ── Extracted Text ───────────────────────────────────────────────────────
    st.subheader("📝 Extracted Text")
    raw_text = processed.get("raw_text", "")
    if raw_text:
        char_count = len(raw_text)
        st.caption(f"{char_count:,} characters extracted")
        with st.expander("View Full Text", expanded=False):
            st.code(raw_text[:50_000], language="text")
            if char_count > 50_000:
                st.caption("ℹ️ Showing first 50,000 characters.")
    else:
        st.info("No text was extracted from this file.")

    st.markdown("---")

    # ── Keywords ─────────────────────────────────────────────────────────────
    st.subheader("🔑 Detected Keywords")
    keywords = processed.get("keywords", {})
    _render_keyword_cards(keywords)

    st.markdown("---")

    # ── Named Entities ───────────────────────────────────────────────────────
    st.subheader("🏷️ Named Entities")
    entities = processed.get("entities", {})
    _render_entity_cards(entities)


def _render_keyword_cards(keywords: dict) -> None:
    """Render keyword categories as styled cards in a grid."""
    if not keywords or all(len(v) == 0 for v in keywords.values()):
        st.info("No keywords detected in this file.")
        return

    cols = st.columns(3)
    col_idx = 0

    for category, values in keywords.items():
        if not values:
            continue
        icon = KEYWORD_ICONS.get(category, "🔤")
        display_name = category.replace("_", " ").title()

        with cols[col_idx % 3]:
            st.markdown(f"""
            <div style="background-color:#262730; padding:15px; border-radius:10px;
                        margin-bottom:10px; border-left:4px solid #0068c9;">
                <h4 style="margin:0 0 8px 0;">{icon} {display_name} ({len(values)})</h4>
                <p style="color:#bbb; font-size:0.9em; margin:0; word-wrap:break-word;">
                    {', '.join(values[:20])}
                    {'...' if len(values) > 20 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1


def _render_entity_cards(entities: dict) -> None:
    """Render entity categories as styled cards in a grid."""
    if not entities or all(len(v) == 0 for v in entities.values()):
        st.info("No named entities detected. Ensure spaCy model (en_core_web_sm) is installed.")
        return

    cols = st.columns(3)
    col_idx = 0

    for category, values in entities.items():
        if not values:
            continue
        icon = ENTITY_ICONS.get(category, "🏷️")
        display_name = category.replace("_", " ").title()

        with cols[col_idx % 3]:
            st.markdown(f"""
            <div style="background-color:#262730; padding:15px; border-radius:10px;
                        margin-bottom:10px; border-left:4px solid #9C27B0;">
                <h4 style="margin:0 0 8px 0;">{icon} {display_name} ({len(values)})</h4>
                <p style="color:#bbb; font-size:0.9em; margin:0; word-wrap:break-word;">
                    {', '.join(values[:20])}
                    {'...' if len(values) > 20 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1
