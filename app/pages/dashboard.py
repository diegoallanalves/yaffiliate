import streamlit as st
import plotly.express as px
from app.components.layout import page_header
from app.repositories.database import read_table
from app.services.scoring import add_opportunity_score
def render():
 page_header("Command centre","Turn research into profitable decisions.","Track products, scenarios, keywords and the next actions required to build your affiliate business.")
 p=add_opportunity_score(read_table("products")); s=read_table("campaign_scenarios"); k=read_table("keywords")
 c1,c2,c3,c4=st.columns(4); c1.metric("Products researched",len(p)); c2.metric("Keywords collected",len(k)); c3.metric("Modelled profit",f"R$ {(s.profit.sum() if not s.empty else 0):,.2f}"); c4.metric("Average ROAS",f"{(s.roas.mean() if not s.empty else 0):.2f}x")
 l,r=st.columns([1.4,1])
 with l:
  st.subheader("Profitability scenarios")
  if s.empty:st.info("Create your first scenario in Profit Calculator.")
  else:st.plotly_chart(px.bar(s.sort_values("created_at"),x="created_at",y="profit",color="product_name"),use_container_width=True)
 with r:
  st.subheader("Top opportunities")
  if p.empty:st.info("Add products in Product Research.")
  else:st.dataframe(p.sort_values("opportunity_score",ascending=False).head(5)[["name","network","opportunity_score","commission","search_volume"]],hide_index=True,use_container_width=True)
 st.subheader("Six-month build status"); st.dataframe([["Month 1","UI, dashboard, calculator, landing pages","In progress"],["Month 2","Product finder, imports, keywords","Planned"],["Month 3","AI copy, SEO, email","Planned"],["Month 4","ML, forecasting, analytics","Planned"],["Month 5","Agents, automation, integrations","Planned"],["Month 6","Auth, payments, deployment, beta","Planned"]],hide_index=True,use_container_width=True)
