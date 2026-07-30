from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from app.components.layout import page_header
from app.services.portfolio_service import PortfolioService


portfolio_service = PortfolioService()

def get_score_icon(score: float) -> str:
    if score >= 80:
        return "🟢"

    if score >= 65:
        return "🟢"

    if score >= 50:
        return "🟡"

    if score >= 35:
        return "🟠"

    return "🔴"


def render() -> None:
    page_header(
        "Portfolio Intelligence",
        "See which products deserve your attention today.",
        (
            "Rank and filter every saved product by opportunity score, "
            "commercial potential and recommended next action."
        ),
    )

    try:
        summary = portfolio_service.get_portfolio_summary()

    except Exception as exc:
        st.error(f"Unable to load portfolio intelligence: {exc}")
        return

    products = summary["products"]

    if not products:
        st.info(
            "No products are available yet. "
            "Add products in Product Research first."
        )
        return

    portfolio_df = pd.DataFrame(products)

    # ---------------------------------------------------------
    # Portfolio overview
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Products analysed",
        summary["total_products"],
    )

    col2.metric(
        "Average score",
        f'{summary["average_score"]:.1f}/100',
    )

    col3.metric(
        "High opportunity",
        summary["high_opportunity"],
    )

    col4.metric(
        "Needs attention",
        summary["needs_attention"],
    )

    st.caption(
        f'Products below 50: {summary["avoid_count"]}'
    )

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------
    st.subheader("Portfolio filters")

    network_values = sorted(
        {
            str(value)
            for value in portfolio_df["NetworkName"].dropna()
        }
    )

    status_values = sorted(
        {
            str(value)
            for value in portfolio_df["Status"].dropna()
        }
    )

    decision_values = sorted(
        {
            str(value)
            for value in portfolio_df["Decision"].dropna()
        }
    )

    filter_col1, filter_col2 = st.columns(2)
    filter_col3, filter_col4 = st.columns(2)

    selected_network = filter_col1.selectbox(
        "Affiliate network",
        options=["All"] + network_values,
    )

    selected_status = filter_col2.selectbox(
        "Product status",
        options=["All"] + status_values,
    )

    minimum_score = filter_col3.slider(
        "Minimum opportunity score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

    selected_decision = filter_col4.selectbox(
        "Decision",
        options=["All"] + decision_values,
    )

    filtered_df = portfolio_df.copy()

    if selected_network != "All":
        filtered_df = filtered_df[
            filtered_df["NetworkName"] == selected_network
        ]

    if selected_status != "All":
        filtered_df = filtered_df[
            filtered_df["Status"] == selected_status
        ]

    if selected_decision != "All":
        filtered_df = filtered_df[
            filtered_df["Decision"] == selected_decision
        ]

    filtered_df = filtered_df[
        filtered_df["OpportunityScore"] >= minimum_score
    ]

    filtered_df = filtered_df.sort_values(
        by="OpportunityScore",
        ascending=False,
    ).reset_index(drop=True)

    filtered_df["Rank"] = filtered_df.index + 1

    st.caption(
        f"Showing {len(filtered_df)} of "
        f'{summary["total_products"]} products.'
    )

    if filtered_df.empty:
        st.warning(
            "No products match the selected filters."
        )
        return

    # ---------------------------------------------------------
    # Top opportunity card based on current filters
    # ---------------------------------------------------------
    top_product = filtered_df.iloc[0].to_dict()

    top_product_name = str(
        top_product.get("ProductName") or "Unnamed product"
    )

    top_network = str(
        top_product.get("NetworkName") or "Not set"
    )

    top_category = str(
        top_product.get("Category") or "Not set"
    )

    top_decision = str(
        top_product.get("Decision") or "Not available"
    )

    top_action = str(
        top_product.get("PriorityAction") or "No action available"
    )

    top_score = float(
        top_product.get("OpportunityScore") or 0
    )

    top_commission = float(
        top_product.get("CommissionAmount") or 0
    )

    top_search_volume = int(
        top_product.get("SearchVolume") or 0
    )

    score_icon = get_score_icon(top_score)

    top_card_html = (
        '<div style="'
        'padding:1.4rem;'
        'border:1px solid rgba(255,255,255,0.10);'
        'border-radius:18px;'
        'background:rgba(18,28,48,0.72);'
        'margin-top:1.2rem;'
        'margin-bottom:1.5rem;'
        '">'
        '<div style="'
        'font-size:0.78rem;'
        'font-weight:700;'
        'letter-spacing:0.08em;'
        'text-transform:uppercase;'
        'color:#a78bfa;'
        'margin-bottom:0.45rem;'
        '">'
        'Top opportunity for current filters'
        '</div>'
        '<div style="'
        'font-size:1.65rem;'
        'font-weight:700;'
        'margin-bottom:0.35rem;'
        '">'
        f'{score_icon} {escape(top_product_name)}'
        '</div>'
        '<div style="'
        'color:#a7b3c7;'
        'font-size:0.95rem;'
        'margin-bottom:1rem;'
        '">'
        f'{escape(top_network)} · {escape(top_category)}'
        '</div>'
        '<div style="'
        'display:grid;'
        'grid-template-columns:repeat(3,1fr);'
        'gap:1rem;'
        'margin-bottom:1rem;'
        '">'
        '<div>'
        '<div style="color:#94a3b8;font-size:0.8rem;">'
        'Opportunity'
        '</div>'
        '<div style="font-size:1.35rem;font-weight:700;">'
        f'{top_score:.1f}/100'
        '</div>'
        '</div>'
        '<div>'
        '<div style="color:#94a3b8;font-size:0.8rem;">'
        'Commission'
        '</div>'
        '<div style="font-size:1.35rem;font-weight:700;">'
        f'R$ {top_commission:,.2f}'
        '</div>'
        '</div>'
        '<div>'
        '<div style="color:#94a3b8;font-size:0.8rem;">'
        'Monthly searches'
        '</div>'
        '<div style="font-size:1.35rem;font-weight:700;">'
        f'{top_search_volume:,}'
        '</div>'
        '</div>'
        '</div>'
        '<div style="'
        'padding:0.85rem 1rem;'
        'border-radius:10px;'
        'background:rgba(139,92,246,0.10);'
        'margin-bottom:0.75rem;'
        '">'
        f'<strong>Decision:</strong> {escape(top_decision)}'
        '</div>'
        '<div style="'
        'padding:0.85rem 1rem;'
        'border-radius:10px;'
        'background:rgba(14,165,233,0.08);'
        '">'
        f'<strong>Recommended action:</strong> {escape(top_action)}'
        '</div>'
        '</div>'
    )

    st.markdown(
        top_card_html,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Ranked portfolio
    # ---------------------------------------------------------
    st.divider()
    st.subheader("Ranked portfolio")

    display_columns = [
        "Rank",
        "ProductName",
        "NetworkName",
        "Category",
        "Status",
        "CommissionAmount",
        "SearchVolume",
        "CompetitionScore",
        "GoogleTrendScore",
        "OpportunityScore",
        "Decision",
        "PriorityAction",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    table_df = filtered_df[available_columns].copy()

    table_df = table_df.rename(
        columns={
            "ProductName": "Product",
            "NetworkName": "Network",
            "CommissionAmount": "Commission",
            "SearchVolume": "Search volume",
            "CompetitionScore": "Competition",
            "GoogleTrendScore": "Trend",
            "OpportunityScore": "Score",
            "PriorityAction": "Priority action",
        }
    )

    st.dataframe(
        table_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank",
                width="small",
                format="%d",
            ),
            "Commission": st.column_config.NumberColumn(
                "Commission",
                format="R$ %.2f",
            ),
            "Search volume": st.column_config.NumberColumn(
                "Search volume",
                format="%d",
            ),
            "Competition": st.column_config.ProgressColumn(
                "Competition",
                min_value=0,
                max_value=100,
                format="%.0f",
            ),
            "Trend": st.column_config.ProgressColumn(
                "Trend",
                min_value=0,
                max_value=100,
                format="%.0f",
            ),
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Priority action": st.column_config.TextColumn(
                "Priority action",
                width="large",
            ),
        },
    )