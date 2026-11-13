
"""Personalized YAffiliate dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.layout import navigate_to, page_header
from app.services.currency_service import convert_currency, format_currency
from app.services.dashboard_service import DashboardService
from app.services.translation_service import ui


def _first_name() -> str:
    email = (
        st.session_state.get("auth_user_email")
        or st.session_state.get("user_email")
        or ""
    )

    name = (
        st.session_state.get("user_name")
        or st.session_state.get("full_name")
        or ""
    )

    if name:
        return str(name).split()[0].title()

    if email:
        return str(email).split("@")[0].split(".")[0].title()

    return "there"


def _scenario_chart_data(scenarios, currency):
    rows = []

    if scenarios.empty:
        return pd.DataFrame()

    for index, scenario in scenarios.iterrows():
        source = scenario.get("currency_code")

        if pd.isna(source) or not str(source).strip():
            continue

        source = str(source).strip().upper()

        profit = convert_currency(
            scenario.get("profit"),
            source,
            currency,
        )

        budget = convert_currency(
            scenario.get("budget"),
            source,
            currency,
        )

        revenue = convert_currency(
            scenario.get("revenue"),
            source,
            currency,
        )

        if any(value is None for value in (profit, budget, revenue)):
            continue

        rows.append(
            {
                "Scenario": f"Scenario {index + 1}",
                "Product": str(
                    scenario.get("product_name") or "Product"
                ),
                "Budget": float(budget),
                "Revenue": float(revenue),
                "Profit": float(profit),
            }
        )

    return pd.DataFrame(rows)


def render() -> None:
    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error(ui("Please sign in again."))
        return

    try:
        service = DashboardService(user_id=str(user_id))
        snapshot = service.get_snapshot()
    except Exception as error:
        st.error(ui("Dashboard data could not be loaded."))
        st.exception(error)
        return

    currency = snapshot.reporting_currency
    name = _first_name()

    page_header(
        "YOUR WORKSPACE",
        f"Welcome back, {name}!",
        "Your products, campaigns and marketing performance in one place.",
    )

    # Main performance metrics
    a, b, c, d = st.columns(4)

    a.metric(
        "Products researched",
        len(snapshot.products),
    )

    b.metric(
        "Saved campaigns",
        snapshot.campaign_count,
    )

    c.metric(
        "Modelled profit",
        format_currency(snapshot.modelled_profit, currency),
    )

    d.metric(
        "Campaign ROAS",
        f"{snapshot.average_roas:.2f}x",
    )

    st.caption(
        f"Reporting currency: {currency} · "
        "Financial results are estimates, not actual earnings."
    )

    if snapshot.excluded_scenario_count:
        st.warning(
            f"{snapshot.excluded_scenario_count} scenario(s) excluded "
            "from financial metrics because currency or exchange-rate "
            "information is unavailable."
        )

    st.divider()

    # Visual analytics
    st.subheader("Performance overview")

    chart_data = _scenario_chart_data(
        snapshot.scenarios,
        currency,
    )

    left, right = st.columns([1.5, 1])

    with left:
        if not chart_data.empty:
            fig = px.bar(
                chart_data,
                x="Product",
                y=["Budget", "Revenue", "Profit"],
                barmode="group",
                title="Campaign financial comparison",
                labels={
                    "value": f"Amount ({currency})",
                    "variable": "Metric",
                },
                color_discrete_sequence=[
                    "#64748b",
                    "#8b5cf6",
                    "#22c55e",
                ],
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=50, b=10),
                legend_title_text="",
                height=340,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            with st.container(border=True):
                st.info(
                    "Save a Profit Calculator scenario to see "
                    "your financial charts here."
                )

    with right:
        if not chart_data.empty:
            totals = chart_data[
                ["Budget", "Revenue", "Profit"]
            ].sum()

            fig = px.pie(
                names=["Budget", "Revenue"],
                values=[
                    max(float(totals["Budget"]), 0),
                    max(float(totals["Revenue"]), 0),
                ],
                hole=0.65,
                title="Modelled spending vs revenue",
                color_discrete_sequence=[
                    "#8b5cf6",
                    "#06b6d4",
                ],
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=50, b=10),
                height=340,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            with st.container(border=True):
                st.info("Your campaign breakdown will appear here.")

    st.divider()

    # Recent work
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Recent campaigns")

        if not snapshot.campaigns:
            st.info("Your saved campaigns will appear here.")
        else:
            for campaign in snapshot.campaigns[:3]:
                campaign_id = campaign.get("id")

                campaign_name = service.campaign_display_name(
                    campaign
                )

                product_name = campaign.get(
                    "product_name",
                    "Product",
                )

                created = str(
                    campaign.get("created_at") or ""
                )[:10]

                with st.container(border=True):
                    title_col, action_col = st.columns([3, 1])

                    with title_col:
                        st.markdown(f"**{campaign_name}**")
                        st.caption(f"{product_name} · {created}")

                    with action_col:
                        if st.button(
                            "Open",
                            key=f"open_campaign_{campaign_id}",
                            use_container_width=True,
                        ):
                            st.session_state[
                                "campaign_history_selected_id"
                            ] = campaign_id

                            navigate_to("campaign_history")

    with right:
        st.subheader("Your top products")

        products = snapshot.products

        if products.empty:
            st.info(
                "No locally researched products yet. "
                "Start with Product Research."
            )
        else:
            columns = [
                column
                for column in [
                    "name",
                    "network",
                    "opportunity_score",
                    "commission",
                ]
                if column in products.columns
            ]

            if "opportunity_score" in products.columns:
                products = products.sort_values(
                    "opportunity_score",
                    ascending=False,
                )

            st.dataframe(
                products.head(5)[columns],
                hide_index=True,
                use_container_width=True,
            )

    st.divider()

    # One primary action, not multiple competing buttons
    st.subheader("What's next?")

    st.caption(
        "Discover products, build a campaign, "
        "or review your financial performance."
    )

    action = st.selectbox(
        "Choose your next action",
        [
            "Discover products",
            "Generate a campaign",
            "Profit Calculator",
            "View analytics",
            "Campaign history",
        ],
        label_visibility="collapsed",
    )

    routes = {
        "Discover products": "product_discovery",
        "Generate a campaign": "quick_generate",
        "Profit Calculator": "profit_calculator",
        "View analytics": "analytics",
        "Campaign history": "campaign_history",
    }

    if st.button(
        "Continue",
        type="primary",
        use_container_width=True,
    ):
        navigate_to(routes[action])
