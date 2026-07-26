"""
upload_view.py — Upload Evidence page for CaseMind AI.

Provides a drag-and-drop file upload interface, validates file types,
saves files to categorized folders, stores metadata in the database,
automatically processes files for text extraction, keyword & entity analysis,
and displays the Evidence Manager with global search below.
"""

import streamlit as st
from datetime import datetime
from modules.database import init_db, add_evidence, add_processed_evidence
from modules.file_utils import is_supported_file, save_uploaded_file, format_filesize
from modules.text_extractor import extract_text
from modules.keyword_extractor import extract_keywords
from modules.entity_extractor import extract_entities
from modules.upload_manager import render_evidence_manager
from modules.search_engine import global_search, highlight_query


def render() -> None:
    """Render the Upload Evidence page."""
    # Ensure the database is initialized
    init_db()

    st.title("📂 Upload Evidence")
    st.write("Securely upload digital evidence for analysis. "
             "Our system automatically processes and categorizes your files.")
    st.markdown("---")

    # ── Global Search Bar ────────────────────────────────────────────────────
    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        search_query = st.text_input(
            "🔍 Global Search",
            placeholder="Search across all extracted text...",
            key="global_search_input",
            label_visibility="collapsed",
        )
    with search_col2:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

    if search_query and search_clicked:
        _render_search_results(search_query)

    st.markdown("---")

    # ── Drag-and-drop styled area ────────────────────────────────────────────
    st.markdown("""
        <div style="background-color: #262730; padding: 30px; border-radius: 12px;
                    border: 2px dashed #0068c9; text-align: center; margin-bottom: 10px;">
            <h3 style="margin-bottom: 5px;">📤 Drag and drop files here</h3>
            <p style="color: #888; margin: 0;">Limit 200MB per file</p>
        </div>
    """, unsafe_allow_html=True)

    # ── File uploader ────────────────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "Or browse files",
        type=["pdf", "png", "jpg", "jpeg", "txt", "csv", "eml"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.info("📎 Supported file types: **PDF**, **Image** (PNG/JPG), **TXT**, **CSV**, **EML**")

    # ── Process uploaded files ───────────────────────────────────────────────
    if uploaded_files:
        _process_uploads(uploaded_files)

    # ── Evidence Manager table ───────────────────────────────────────────────
    render_evidence_manager()


def _process_uploads(uploaded_files: list) -> None:
    """Validate, save, record, and automatically process each uploaded file."""
    # Track which files have already been processed this session
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()

    new_uploads = []
    case_id = st.session_state.get("active_case_id", "default")
    for uf in uploaded_files:
        file_key = f"{case_id}_{uf.name}_{uf.size}"
        if file_key in st.session_state.processed_files:
            continue
        if not is_supported_file(uf.name):
            st.error(f"❌ **{uf.name}** — Unsupported file type.")
            continue
        new_uploads.append((uf, file_key))

    if not new_uploads:
        return

    progress = st.progress(0, text="Uploading and processing files...")
    total = len(new_uploads)

    for idx, (uf, file_key) in enumerate(new_uploads):
        try:
            # ── Step 1: Save file ────────────────────────────────────────────
            final_name, filepath, filetype, filesize, was_renamed = save_uploaded_file(uf)
            upload_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

            evidence_id = add_evidence(
                filename=final_name,
                filepath=filepath,
                filetype=filetype,
                filesize=filesize,
                upload_time=upload_time,
            )

            st.session_state.processed_files.add(file_key)

            if was_renamed:
                st.warning(f"⚠️ Duplicate detected — renamed to **{final_name}**")

            # ── Step 2: Extract text ─────────────────────────────────────────
            progress.progress(
                (idx + 0.5) / total,
                text=f"Processing {final_name}..."
            )

            extraction = extract_text(filepath, filetype)
            raw_text = extraction["raw_text"]
            metadata = extraction["metadata"]
            proc_status = extraction["status"]
            error_msg = extraction["error"]

            # ── Step 3: Extract keywords & entities ──────────────────────────
            keywords = {}
            entities = {}
            if proc_status == "Completed" and raw_text:
                keywords = extract_keywords(raw_text)
                try:
                    api_key = st.session_state.get("groq_api_key", "")
                    entities = extract_entities(raw_text, api_key)
                except Exception:
                    entities = {}  # Graceful fallback if extraction fails

            # ── Step 4: Store processed results ──────────────────────────────
            processed_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            add_processed_evidence(
                evidence_id=evidence_id,
                filename=final_name,
                filetype=filetype,
                raw_text=raw_text,
                metadata=metadata,
                keywords=keywords,
                entities=entities,
                processed_time=processed_time,
                processing_status=proc_status,
                error_message=error_msg,
            )

            # ── Notification ─────────────────────────────────────────────────
            if proc_status == "Completed":
                st.success(
                    f"✅ **{final_name}** — {format_filesize(filesize)} — "
                    f"Uploaded & Processed ({extraction['processing_time']}s)"
                )
            else:
                st.error(
                    f"❌ **{final_name}** — Processing failed: {error_msg}"
                )

        except Exception as e:
            st.error(f"❌ Failed to upload **{uf.name}**: {e}")

        progress.progress((idx + 1) / total, text=f"Completed {idx + 1} of {total} files...")

    progress.empty()


def _render_search_results(query: str) -> None:
    """Render global search results."""
    results = global_search(query)

    if not results:
        st.warning(f"No results found for **\"{query}\"**")
        return

    st.success(f"Found **{len(results)}** match(es) for **\"{query}\"**")

    for i, result in enumerate(results[:20]):
        highlighted = highlight_query(result["snippet"], query)
        st.markdown(f"""
        <div style="background-color:#262730; padding:12px 15px; border-radius:8px;
                    margin-bottom:8px; border-left:4px solid #0068c9;">
            <strong>{result['filename']}</strong>
            <span style="color:#888;"> ({result['filetype'].upper()})</span>
            <span style="color:#666; font-size:0.85em;"> — Line {result['line_number']}</span>
            <p style="color:#ccc; margin:8px 0 0 0; font-size:0.9em;">{highlighted}</p>
        </div>
        """, unsafe_allow_html=True)
