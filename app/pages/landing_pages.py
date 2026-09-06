from app.services.translation_service import ui
import streamlit as st
from app.components.layout import page_header
from app.services.landing_page import generate_html

def render():
    page_header('Conversion studio', 'Create compliant affiliate landing pages.', 'Generate clean HTML while keeping claims truthful and relationships transparent.')
    st.warning(ui('Do not invent testimonials, guarantees, scarcity, medical outcomes, income claims or discounts.'))
    with st.form('lp'):
        product = st.text_input(ui('Product name'))
        audience = st.text_input(ui('Target audience'))
        benefit = st.text_input(ui('Main truthful benefit'))
        cta = st.text_input(ui('Call to action'), 'View the official offer')
        url = st.text_input(ui('Affiliate URL'), 'https://example.com')
        ok = st.form_submit_button(ui('Generate landing page'), use_container_width=True)
    if ok:
        if not product or not audience or (not benefit):
            st.error(ui('Complete product, audience and benefit.'))
            return
        html, path = generate_html(product, audience, benefit, cta, url)
        st.success(f'Saved to: {path}')
        st.components.v1.html(html, height=680, scrolling=True)
        st.download_button(ui('Download HTML'), html.encode(), Path(path).name, 'text/html')
from pathlib import Path
