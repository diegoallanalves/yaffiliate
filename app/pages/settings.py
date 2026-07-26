import os,streamlit as st
from app.components.layout import page_header
from app.repositories.database import get_setting,upsert_setting
def render():
 page_header("Workspace controls","Configure the development environment.","Store non-secret preferences here; keep API keys in .env.")
 with st.form("settings"):
  name=st.text_input("Workspace name",get_setting("workspace_name","Diego Affiliate Lab")); currency=st.selectbox("Default currency",["BRL","USD","EUR","GBP"]); budget=st.number_input("Default monthly testing budget",min_value=0.0,value=float(get_setting("monthly_budget","1000")),step=100.0); ok=st.form_submit_button("Save settings")
 if ok:upsert_setting("workspace_name",name);upsert_setting("currency",currency);upsert_setting("monthly_budget",str(budget));st.success("Settings saved.")
 st.subheader("Integration status"); st.write("OpenAI API:","Configured" if os.getenv("OPENAI_API_KEY") else "Not configured"); st.write("Database: SQLite local development"); st.write("Authentication: Month 6"); st.write("Payments: Month 6")
