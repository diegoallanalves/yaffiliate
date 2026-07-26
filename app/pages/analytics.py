import streamlit as st
import plotly.express as px
from app.components.layout import page_header
from app.repositories.database import read_table
def render():
 page_header("Performance intelligence","Understand your modelled campaign economics.","Later this will combine ad-platform, network and website data.")
 df=read_table("campaign_scenarios")
 if df.empty:st.info("Save calculator scenarios first."); return
 budget=df.budget.sum(); revenue=df.revenue.sum(); profit=df.profit.sum(); roas=revenue/budget if budget else 0
 a,b,c,d=st.columns(4); a.metric("Scenarios",len(df)); b.metric("Budget",f"R$ {budget:,.2f}"); c.metric("Profit",f"R$ {profit:,.2f}"); d.metric("Weighted ROAS",f"{roas:.2f}x")
 st.plotly_chart(px.scatter(df,x="budget",y="profit",size="revenue",color="roas",hover_name="product_name"),use_container_width=True); st.dataframe(df,hide_index=True,use_container_width=True); st.download_button("Export analytics CSV",df.to_csv(index=False).encode(),"campaign_analytics.csv","text/csv")
