from app.services.translation_service import ui
import streamlit as st
from app.components.layout import page_header
from app.services.ai import generate_text

def render():
    page_header('Organic growth', 'Plan helpful search content.', 'Create article briefs around real intent instead of low-value pages.')
    kw = st.text_input(ui('Primary keyword'))
    audience = st.text_input(ui('Audience'))
    facts = st.text_area(ui('Verified facts and sources'))
    typ = st.selectbox(ui('Content type'), ['Comparison', 'How-to', 'Review', 'Buying guide', 'FAQ'])
    if st.button(ui('Generate SEO brief'), type='primary'):
        st.markdown(generate_text('Create useful non-spammy SEO briefs and mark unsupported claims.', f'Create a {typ} brief for {kw}, audience {audience}, using only: {facts}.'))
