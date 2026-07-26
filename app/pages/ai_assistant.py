import streamlit as st
from app.components.layout import page_header
from app.services.ai import generate_text
def render():
 page_header("AI workspace","Turn structured research into better decisions.","Analysis and drafting with human review before publication or spending.")
 mode=st.selectbox("Assistant mode",["Product analysis","Campaign diagnosis","Landing-page outline","Keyword clustering","Weekly action plan"]); context=st.text_area("Context",height=220)
 if st.button("Generate analysis",type="primary",use_container_width=True):
  if not context.strip():st.error("Provide context first.")
  else:st.markdown(generate_text("Be precise, separate facts from assumptions and never fabricate performance data.",f"Mode: {mode}\n\nContext:\n{context}"))
