import streamlit as st
from app.components.layout import page_header
from app.services.ai import generate_text
def render():
 page_header("Organic growth","Plan helpful search content.","Create article briefs around real intent instead of low-value pages.")
 kw=st.text_input("Primary keyword"); audience=st.text_input("Audience"); facts=st.text_area("Verified facts and sources"); typ=st.selectbox("Content type",["Comparison","How-to","Review","Buying guide","FAQ"])
 if st.button("Generate SEO brief",type="primary"):st.markdown(generate_text("Create useful non-spammy SEO briefs and mark unsupported claims.",f"Create a {typ} brief for {kw}, audience {audience}, using only: {facts}."))
