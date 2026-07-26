import streamlit as st
from app.components.layout import page_header
from app.services.ai import generate_text
def render():
 page_header("Lifecycle messaging","Draft useful email sequences without spam.","Build permission-based educational and promotional campaigns.")
 a,b=st.columns(2); product=a.text_input("Product"); audience=b.text_input("Audience"); offer=st.text_area("Verified offer details"); typ=st.selectbox("Sequence",["3-email welcome","5-email education","Abandoned interest","Launch sequence"])
 if st.button("Generate email sequence",type="primary"):st.markdown(generate_text("Write ethical permission-based affiliate email and include an unsubscribe reminder.",f"Create a {typ} for {product}, aimed at {audience}. Use only: {offer}."))
