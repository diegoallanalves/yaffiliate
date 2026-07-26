from pathlib import Path
import streamlit as st
from app.repositories.database import initialise_database

def bootstrap_app():
    st.set_page_config(page_title="Filtrify AI",page_icon="⚡",layout="wide",initial_sidebar_state="expanded")
    css=Path(__file__).resolve().parents[1]/"assets"/"app.css"
    st.markdown(css.read_text(encoding="utf-8"),unsafe_allow_html=True)
    initialise_database()
