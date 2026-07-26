import streamlit as st
import plotly.express as px
from app.components.layout import page_header
from app.repositories.database import insert_record,read_table,delete_record
def render():
 page_header("Search intelligence","Build a commercial keyword database.","Capture intent, volume, CPC and competition before connecting approved keyword APIs.")
 with st.form("kw",clear_on_submit=True):
  a,b,c=st.columns(3); keyword=a.text_input("Keyword"); intent=b.selectbox("Intent",["Informational","Commercial","Transactional","Navigational"]); product=c.text_input("Related product")
  a,b,c=st.columns(3); volume=a.number_input("Monthly volume",min_value=0,step=100); cpc=b.number_input("Estimated CPC",min_value=0.0); comp=c.number_input("Competition 0-100",min_value=0.0,max_value=100.0); status=st.selectbox("Status",["Idea","Review","Target","Negative","Published"]); ok=st.form_submit_button("Save keyword",use_container_width=True)
 if ok:
  if not keyword.strip():st.error("Keyword is required.")
  else:insert_record("keywords",{"keyword":keyword.strip(),"intent":intent,"volume":int(volume),"cpc":cpc,"competition":comp,"product_name":product,"status":status}); st.rerun()
 df=read_table("keywords")
 if df.empty:st.info("No keywords saved yet."); return
 st.plotly_chart(px.scatter(df,x="competition",y="cpc",size="volume",color="intent",hover_name="keyword"),use_container_width=True); st.dataframe(df,hide_index=True,use_container_width=True); st.download_button("Export keywords CSV",df.to_csv(index=False).encode(),"keywords.csv","text/csv")
 rid=st.number_input("Keyword ID to delete",min_value=0,step=1);
 if st.button("Delete selected keyword") and rid>0:delete_record("keywords",int(rid)); st.rerun()
