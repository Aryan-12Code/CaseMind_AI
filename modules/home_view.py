"""
home_view.py — The Case Dashboard for CaseMind AI.

Displays the list of recent investigations, allows creating new cases,
and managing existing ones (rename, archive, delete, open).
"""

import streamlit as st
from modules.cases_db import (
    init_master_db,
    create_case,
    get_all_cases,
    rename_case,
    update_case_status,
    delete_case
)
from modules.file_utils import delete_case_files
import shutil
import os
import time
import html as _html


def render() -> None:
    """Render the Home/Case Selection page."""
    init_master_db()

    st.title("🛡️ CaseMind AI - Investigations")
    st.write("Manage your digital evidence investigation cases.")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("➕ New Case")
        with st.form("new_case_form"):
            new_name = st.text_input("Case Name", placeholder="e.g. Cyber Fraud 2026")
            submitted = st.form_submit_button("Create Case", type="primary", use_container_width=True)
            if submitted:
                if new_name.strip():
                    case_id = create_case(new_name.strip())
                    st.toast(f"✓ Case '{new_name}' created!")
                    st.session_state["active_case_id"] = case_id
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Case name cannot be empty.")

    with col1:
        st.subheader("📂 Recent Investigations")
        
        cases = get_all_cases()
        
        if not cases:
            st.info("No cases found. Create a new case to get started.")
            return

        for case in cases:
            _render_case_card(case)


def _render_case_card(case: dict) -> None:
    """Render a single case as a styled card with actions."""
    
    # Determine status color
    status = case["status"]
    if status == "Completed":
        status_color = "#4CAF50"
    elif status == "Archived":
        status_color = "#9E9E9E"
    else:
        status_color = "#FFC107" # In Progress

    safe_name = _html.escape(case['name'])
    safe_status = _html.escape(status)

    st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; margin-bottom:15px; border-left:5px solid {status_color};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0;">{safe_name}</h3>
            <span style="color:{status_color}; font-weight:bold; font-size:0.9em; padding:4px 12px; border:1px solid {status_color}; border-radius:15px;">
                {safe_status}
            </span>
        </div>
        <p style="color:#888; font-size:0.9em; margin:5px 0 15px 0;">
            Updated: {case['updated_at']} | Created: {case['created_at']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col_open, col_rename, col_status, col_del = st.columns([2, 2, 2, 1])
    
    with col_open:
        if st.button("📂 Open Case", key=f"open_{case['id']}", use_container_width=True, type="primary"):
            st.session_state["active_case_id"] = case["id"]
            st.rerun()
            
    with col_rename:
        with st.popover("✏️ Rename", use_container_width=True):
            new_name = st.text_input("New Name", value=case['name'], key=f"rn_in_{case['id']}")
            if st.button("Save", key=f"rn_btn_{case['id']}"):
                if new_name.strip():
                    rename_case(case['id'], new_name.strip())
                    st.toast("✓ Case renamed.")
                    st.rerun()

    with col_status:
        with st.popover("🔄 Status", use_container_width=True):
            status_options = ["In Progress", "Completed", "Archived"]
            status_idx = status_options.index(status) if status in status_options else 0
            new_status = st.selectbox(
                "Set Status", 
                status_options, 
                index=status_idx,
                key=f"st_sel_{case['id']}"
            )
            if st.button("Update", key=f"st_btn_{case['id']}"):
                update_case_status(case['id'], new_status)
                st.toast("✓ Status updated.")
                st.rerun()
                
    with col_del:
        with st.popover("🗑️", use_container_width=True):
            st.warning("Delete this case forever? This deletes all files and database records.")
            if st.button("Confirm Delete", key=f"del_btn_{case['id']}", type="primary"):
                delete_case_files(case['id'])
                # Also clean up the case's isolated database
                _db_case_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "database", "cases", str(case['id'])
                )
                if os.path.exists(_db_case_dir):
                    shutil.rmtree(_db_case_dir, ignore_errors=True)
                delete_case(case['id'])
                st.toast("✓ Case deleted.")
                st.rerun()
                
    st.write("") # spacing
