import streamlit as st
from app.components.layout import page_header
from app.repositories.database import read_table
from app.services.scoring import add_opportunity_score
def render():
 page_header("Product catalogue","Manage your affiliate shortlist.","Portfolio view of researched, tested and active products.")
 df=add_opportunity_score(read_table("products"))
 if df.empty:st.info("Add products in Product Research."); return
 statuses=["All"]+sorted(df.status.dropna().unique().tolist()); selected=st.selectbox("Filter by status",statuses); f=df if selected=="All" else df[df.status==selected]
 for _,r in f.sort_values("opportunity_score",ascending=False).iterrows():st.markdown(f'<div class="card"><span class="chip">{r.status}</span><h3>{r["name"]}</h3><p>{r.network or "Network not set"} · {r.category or "Category not set"}</p><p><b>Score:</b> {r.opportunity_score}/100<br><b>Commission:</b> R$ {r.commission:,.2f}<br><b>Search volume:</b> {int(r.search_volume):,}</p></div>',unsafe_allow_html=True)
