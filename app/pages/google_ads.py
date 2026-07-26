import streamlit as st
from app.components.layout import page_header
from app.services.ai import generate_text
def render():
 page_header("Paid acquisition","Prepare Google Ads assets before launch.","Draft ad groups and negatives, then review platform and network rules.")
 product=st.text_input("Product"); lp=st.text_input("Landing-page URL"); facts=st.text_area("Verified product facts"); kws=st.text_area("Target keywords")
 if st.button("Draft campaign structure",type="primary"):st.markdown(generate_text("Draft compliant search ads without unsupported claims.",f"Product: {product}\nLanding page: {lp}\nFacts: {facts}\nKeywords: {kws}"))
