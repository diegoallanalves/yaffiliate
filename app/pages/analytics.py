
"""Currency-aware campaign performance analytics."""

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.layout import page_header
from app.repositories.database import get_setting, read_table
from app.services.currency_service import (
    SUPPORTED_CURRENCIES,
    convert_currency,
    format_currency,
)
from app.services.translation_service import ui


def render():
    page_header(
        "Performance intelligence",
        "Understand your modelled campaign economics.",
        "Compare scenarios using a single reporting currency.",
    )

    df = read_table("campaign_scenarios")

    if df.empty:
        st.info(ui("Save calculator scenarios first."))
        return

    currency = str(
        get_setting("currency", "BRL") or "BRL"
    ).strip().upper()

    if currency not in SUPPORTED_CURRENCIES:
        currency = "BRL"

    rows = []
    excluded = 0

    for _, row in df.iterrows():
        source = row.get("currency_code")
        source = str(source).strip().upper() if pd.notna(source) else ""

        if source not in SUPPORTED_CURRENCIES:
            excluded += 1
            continue

        try:
            budget = float(row["budget"])
            revenue = float(row["revenue"])
            profit = float(row["profit"])
        except (KeyError, TypeError, ValueError):
            excluded += 1
            continue

        converted = [
            convert_currency(value, source, currency)
            for value in (budget, revenue, profit)
        ]

        if any(value is None for value in converted):
            excluded += 1
            continue

        budget, revenue, profit = map(float, converted)

        rows.append({
            "product_name": row.get("product_name", "Product"),
            "source_currency": source,
            "reporting_currency": currency,
            "budget": budget,
            "revenue": revenue,
            "profit": profit,
            "roas": revenue / budget if budget > 0 else 0,
        })

    st.caption(f"Reporting currency: {currency}")

    if excluded:
        st.warning(
            f"{excluded} scenario(s) excluded because of missing currency, "
            "invalid amounts, or unavailable exchange rates."
        )

    if not rows:
        st.info("No scenarios available for currency-aware analytics.")
        return

    analytics = pd.DataFrame(rows)

    budget = analytics["budget"].sum()
    revenue = analytics["revenue"].sum()
    profit = analytics["profit"].sum()
    roas = revenue / budget if budget > 0 else 0

    a, b, c, d = st.columns(4)

    a.metric(ui("Scenarios"), len(analytics))
    b.metric(ui("Budget"), format_currency(budget, currency))
    c.metric(ui("Profit"), format_currency(profit, currency))
    d.metric(ui("Weighted ROAS"), f"{roas:.2f}x")

    st.plotly_chart(
        px.scatter(
            analytics,
            x="budget",
            y="profit",
            size="revenue",
            color="roas",
            hover_name="product_name",
            labels={
                "budget": f"Budget ({currency})",
                "profit": f"Profit ({currency})",
                "revenue": f"Revenue ({currency})",
                "roas": "ROAS",
            },
            title="Campaign profitability",
        ),
        use_container_width=True,
    )

    st.dataframe(
        analytics,
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        ui("Export analytics CSV"),
        analytics.to_csv(index=False).encode("utf-8"),
        "campaign_analytics.csv",
        "text/csv",
    )
