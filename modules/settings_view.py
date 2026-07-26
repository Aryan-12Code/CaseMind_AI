"""
settings_view.py — Settings page for CaseMind AI.

Provides UI for configuring the Gemini API key (persisted in session_state),
theme, language, and export preferences.
"""

import streamlit as st
from modules.ai_engine import test_connection
from modules.config_manager import load_config, save_config, sync_config_to_session


def render() -> None:
    """Render the Settings page."""
    sync_config_to_session()
    st.title("⚙ Settings")
    st.write("Configure application preferences.")
    st.markdown("---")

    # ── API Integration ──────────────────────────────────────────────────────
    st.subheader("🔑 AI Integration — Groq Engine")

    current_key = st.session_state.get("groq_api_key", "")
    api_key = st.text_input(
        "Groq API Key",
        value=current_key,
        type="password",
        placeholder="gsk_...",
        help="Get a free key at https://console.groq.com/keys",
    )

    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 Save Key", type="primary", use_container_width=True):
            if api_key:
                st.session_state["groq_api_key"] = api_key
                st.success("✅ API key saved for this session.")
            else:
                st.warning("⚠️ Please enter an API key.")

    with col2:
        if st.button("🔌 Test Connection", use_container_width=True):
            if api_key:
                with st.spinner("Testing connection..."):
                    success, message = test_connection(api_key)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("⚠️ Enter an API key first.")

    if current_key:
        st.caption(f"✅ API key is set ({len(current_key)} characters)")
    else:
        st.caption("⚠️ No API key set. AI features are disabled.")

    st.markdown("---")

    # ── Application Settings ─────────────────────────────────────────────────
    st.subheader("🏢 Application Settings")
    
    company_name = st.text_input("Company / Agency Name", value=st.session_state.get("company_name", ""), help="This will appear on the cover page of generated reports.")
    
    col_theme, col_lang = st.columns(2)
    with col_theme:
        theme_options = ["Dark Mode", "Light Mode", "System Default"]
        current_theme = st.session_state.get("theme", "System Default")
        theme_index = theme_options.index(current_theme) if current_theme in theme_options else 2
        theme = st.selectbox("Theme", theme_options, index=theme_index)
    with col_lang:
        lang_options = ["English", "Spanish", "French", "German"]
        current_lang = st.session_state.get("language", "English")
        lang_index = lang_options.index(current_lang) if current_lang in lang_options else 0
        language = st.selectbox("Language", lang_options, index=lang_index)

    st.markdown("---")

    # ── Export & Behaviors ───────────────────────────────────────────────────
    st.subheader("📦 Preferences")
    
    col_export, col_autosave = st.columns(2)
    with col_export:
        export_options = ["PDF", "DOCX", "HTML"]
        current_export = st.session_state.get("default_export_format", "PDF")
        export_index = export_options.index(current_export) if current_export in export_options else 0
        export_format = st.selectbox("Default Export Format", export_options, index=export_index)
    with col_autosave:
        st.write("")
        st.write("")
        auto_save = st.checkbox("Enable Auto-Save", value=st.session_state.get("auto_save", True))

    st.write("")
    if st.button("💾 Save Application Settings", type="primary"):
        new_config = {
            "company_name": company_name,
            "theme": theme,
            "language": language,
            "auto_save": auto_save,
            "default_export_format": export_format
        }
        if save_config(new_config):
            # Update session state immediately
            for k, v in new_config.items():
                st.session_state[k] = v
            st.toast("✓ Settings saved successfully!")
            st.success("Settings have been applied and saved globally.")
        else:
            st.error("Failed to save settings to disk.")
