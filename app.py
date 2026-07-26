import streamlit as st
from streamlit_option_menu import option_menu
from modules import (
    home_view,
    dashboard_view,
    upload_view,
    analytics_view,
    graph_view,
    timeline_view,
    chat_view,
    reports_view,
    settings_view,
    evidence_details_view,
    entity_explorer_view,
    keyword_analytics_view,
    about_view,
)
from modules.cases_db import get_case_by_id

# Set page config
st.set_page_config(
    page_title="CaseMind AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-inject API Key from environment (never hardcode secrets!)
import os as _os
if "groq_api_key" not in st.session_state:
    st.session_state["groq_api_key"] = _os.environ.get("GROQ_API_KEY", "")

# Custom CSS for modern dashboard
def load_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stMetric {
            background-color: #262730;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# ── Check if we should show Evidence Details (triggered from upload_manager) ─
if st.session_state.get("view_details_id"):
    evidence_details_view.render(st.session_state["view_details_id"])

# ── Check for Active Case ────────────────────────────────────────────────────
elif not st.session_state.get("active_case_id"):
    # No active case, show the Case Manager Home View
    home_view.render()
    
else:
    # A case is active. Get its name for the sidebar.
    case_info = get_case_by_id(st.session_state["active_case_id"])
    case_name = case_info["name"] if case_info else "Unknown Case"
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🛡️ CaseMind AI")
        st.markdown(f"**Case:** `{case_name}`")
        if st.button("⬅️ Close Case", use_container_width=True):
            st.session_state.pop("active_case_id", None)
            st.rerun()
            
        st.markdown("---")
        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", 
                "Upload Evidence", 
                "Analytics",
                "Entity Explorer",
                "Keyword Analytics",
                "Relationship Graph", 
                "Timeline", 
                "AI Chat", 
                "Investigation Reports", 
                "Settings",
                "About"
            ],
            icons=[
                "house", 
                "cloud-upload", 
                "bar-chart",
                "folder2-open",
                "key",
                "diagram-3", 
                "clock", 
                "chat-dots", 
                "file-earmark-text", 
                "gear",
                "info-circle"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "white", "font-size": "16px"}, 
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                "nav-link-selected": {"background-color": "#0068c9"},
            }
        )

    # Routing with global Error Boundary
    try:
        if selected == "Dashboard":
            dashboard_view.render()
        elif selected == "Upload Evidence":
            upload_view.render()
        elif selected == "Analytics":
            analytics_view.render()
        elif selected == "Entity Explorer":
            entity_explorer_view.render()
        elif selected == "Keyword Analytics":
            keyword_analytics_view.render()
        elif selected == "Relationship Graph":
            graph_view.render()
        elif selected == "Timeline":
            timeline_view.render()
        elif selected == "AI Chat":
            chat_view.render()
        elif selected == "Investigation Reports":
            reports_view.render()
        elif selected == "Settings":
            settings_view.render()
        elif selected == "About":
            about_view.render()
    except Exception as e:
        st.error(f"⚠️ Application Error: {str(e)}")
        st.info("If this error persists, try restarting the application or closing the current case.")

