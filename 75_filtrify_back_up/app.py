from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import initialise_database, load_campaign_scenarios, save_campaign_scenario
from src.features.calculator import calculate_campaign
from src.features.dashboard import prepare_dashboard_data
from src.features.landing_page import build_landing_page

st.set_page_config(
    page_title="Affiliate AI Platform",
    page_icon="🏄",
    layout="wide",
)

initialise_database()

st.title("Affiliate AI Platform")
st.caption("Build one connected product, feature by feature.")

page = st.sidebar.radio(
    "Month 1",
    ["Calculator", "Dashboard", "Landing Page Generator", "Roadmap"],
)

if page == "Calculator":
    st.header("Campaign Profitability Calculator")

    with st.form("calculator"):
        product_name = st.text_input("Product name", "Example product")
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("Ad budget (R$)", min_value=0.0, value=500.0, step=50.0)
            cpc = st.number_input("Average CPC (R$)", min_value=0.01, value=1.50, step=0.10)
        with col2:
            conversion_rate = st.number_input(
                "Conversion rate (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1
            )
            commission = st.number_input(
                "Commission per sale (R$)", min_value=0.01, value=120.0, step=10.0
            )

        submitted = st.form_submit_button("Calculate")

    if submitted:
        try:
            result = calculate_campaign(
                product_name, budget, cpc, conversion_rate, commission
            )
            st.session_state["latest_result"] = result
        except ValueError as exc:
            st.error(str(exc))

    result = st.session_state.get("latest_result")
    if result:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Clicks", f"{result.clicks:,.0f}")
        m2.metric("Expected sales", f"{result.sales:,.2f}")
        m3.metric("Revenue", f"R$ {result.revenue:,.2f}")
        m4.metric("Profit", f"R$ {result.profit:,.2f}")

        st.write(f"**ROAS:** {result.roas:.2f}x")
        st.write(f"**ROI:** {result.roi * 100:.2f}%")
        st.write(
            f"**Break-even conversion rate:** "
            f"{result.break_even_conversion_rate * 100:.2f}%"
        )

        if st.button("Save scenario"):
            save_campaign_scenario(result.as_record())
            st.success("Scenario saved.")

elif page == "Dashboard":
    st.header("Saved Campaign Dashboard")
    df = prepare_dashboard_data(load_campaign_scenarios())

    if df.empty:
        st.info("Save at least one calculator scenario to populate the dashboard.")
    else:
        total_budget = df["budget"].sum()
        total_revenue = df["revenue"].sum()
        total_profit = df["profit"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Modelled budget", f"R$ {total_budget:,.2f}")
        c2.metric("Modelled revenue", f"R$ {total_revenue:,.2f}")
        c3.metric("Modelled profit", f"R$ {total_profit:,.2f}")

        fig = px.bar(
            df.sort_values("created_at"),
            x="created_at",
            y="profit",
            color="product_name",
            title="Modelled profit by saved scenario",
        )
        st.plotly_chart(fig, use_container_width="stretch")

        display_columns = [
            "created_at", "product_name", "budget", "cpc",
            "conversion_rate_percent", "commission", "revenue",
            "profit", "roas", "roi_percent",
        ]
        st.dataframe(df[display_columns], use_container_width="stretch")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download scenarios as CSV",
            data=csv,
            file_name="campaign_scenarios.csv",
            mime="text/csv",
        )

elif page == "Landing Page Generator":
    st.header("Landing Page Generator")
    st.warning(
        "Use only truthful, authorised product information. Do not invent results, "
        "testimonials, scarcity, or guarantees."
    )

    with st.form("landing"):
        product_name = st.text_input("Product name")
        audience = st.text_input("Target audience")
        benefit = st.text_input("Main truthful benefit")
        cta = st.text_input("Call to action", "View the official offer")
        affiliate_url = st.text_input("Affiliate URL", "https://example.com")
        generate = st.form_submit_button("Generate HTML")

    if generate:
        if not product_name or not audience or not benefit:
            st.error("Complete the product, audience and benefit fields.")
        else:
            html, path = build_landing_page(
                product_name, audience, benefit, cta, affiliate_url
            )
            st.success(f"Landing page created: {path}")
            st.components.v1.html(html, height=650, scrolling=True)
            st.download_button(
                "Download HTML",
                data=html.encode("utf-8"),
                file_name=path.split("\\")[-1].split("/")[-1],
                mime="text/html",
            )

else:
    st.header("Six-Month Product Roadmap")
    roadmap = pd.DataFrame(
        [
            (1, "Calculator, dashboard, landing-page generator"),
            (2, "Product finder, compliant data collection, keyword engine"),
            (3, "AI copywriter, SEO tools, email generator"),
            (4, "ML recommendations, forecasting, analytics"),
            (5, "AI agents, automation, integrations"),
            (6, "Authentication, payments, deployment, beta launch"),
        ],
        columns=["Month", "Deliverables"],
    )
    st.dataframe(roadmap, hide_index=True, use_container_width=True)

    st.subheader("Immediate sprint")
    st.checkbox("Run the application locally")
    st.checkbox("Create and save three campaign scenarios")
    st.checkbox("Generate one compliant test landing page")
    st.checkbox("Create the Git repository and first commit")
