import streamlit as st
from app.components.layout import page_header
from app.models.calculator import calculate_campaign
from app.repositories.database import insert_record,read_table
def render():
 page_header("Unit economics","Know your break-even point before spending.","Model profitability using CPC, conversion rate and commission assumptions.")
 p=read_table("products"); names=["Custom product"]+(p.name.tolist() if not p.empty else [])
 with st.form("calc"):
  selected=st.selectbox("Product",names); name=st.text_input("Custom product name","Test product") if selected=="Custom product" else selected
  a,b=st.columns(2); budget=a.number_input("Budget (R$)",min_value=0.0,value=500.0,step=50.0); cpc=a.number_input("Average CPC",min_value=.01,value=1.5); cr=b.number_input("Conversion rate %",min_value=0.0,max_value=100.0,value=2.0); commission=b.number_input("Commission",min_value=.01,value=120.0); ok=st.form_submit_button("Calculate scenario",use_container_width=True)
 if ok:
  try:st.session_state.result=calculate_campaign(name,budget,cpc,cr,commission)
  except ValueError as e:st.error(str(e))
 r=st.session_state.get("result")
 if not r:return
 a,b,c,d=st.columns(4); a.metric("Clicks",f"{r.clicks:,.0f}"); b.metric("Expected sales",f"{r.sales:,.2f}"); c.metric("Revenue",f"R$ {r.revenue:,.2f}"); d.metric("Profit",f"R$ {r.profit:,.2f}")
 a,b,c=st.columns(3); a.metric("ROAS",f"{r.roas:.2f}x"); b.metric("ROI",f"{r.roi*100:.2f}%"); c.metric("Break-even conversion",f"{r.break_even_conversion_rate*100:.2f}%")
 st.caption("Modelled estimates, not guaranteed results.")
 if st.button("Save scenario",type="primary"):insert_record("campaign_scenarios",r.as_record()); st.success("Scenario saved.")
