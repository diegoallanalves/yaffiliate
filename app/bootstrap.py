from pathlib import Path

import streamlit as st

from app.repositories.database import initialise_database


def bootstrap_app() -> None:
    """Configure and initialise the YAffiliate application."""

    st.set_page_config(
        page_title="🚀 YAffiliate",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load the global YAffiliate CSS.
    css_path = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "app.css"
    )

    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

    initialise_database()