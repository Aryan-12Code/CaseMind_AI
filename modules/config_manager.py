"""
config_manager.py — Global configuration manager for CaseMind AI.

Persists application settings (Company Name, Theme, Language) to a local JSON file.
"""

import os
import json
import streamlit as st

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "company_name": "",
    "theme": "System Default",
    "language": "English",
    "auto_save": True,
    "default_export_format": "PDF"
}


def load_config() -> dict:
    """Load configuration from disk or return defaults."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Merge with defaults in case of missing keys
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(new_config: dict) -> bool:
    """Save configuration to disk."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def sync_config_to_session() -> None:
    """Load config and inject it into st.session_state if not already present."""
    config = load_config()
    for k, v in config.items():
        if k not in st.session_state:
            st.session_state[k] = v
