
import streamlit as st

from app.components.layout import page_header
from app.models.calculator import calculate_campaign
from app.repositories.database import insert_record, read_table
from app.services.currency_service import format_currency
from app.services.translation_service import ui


CURRENCIES = ["BRL", "USD", "EUR", "GBP"]


def render():
    page_header(
        "Unit economics",
        "Know your break-even point before spending.",
        "Model profitability using CPC, conversion rate and commission assumptions.",
    )

    products = read_table("products")
    names = ["Custom product"] + (
        products["name"].dropna().tolist()
        if not products.empty else []
    )

    selected = st.selectbox(ui("Product"), names)

    product = None
    if selected != "Custom product":
        matches = products[products["name"] == selected]
        if not matches.empty:
            product = matches.iloc[0]

    name = (
        st.text_input(ui("Custom product name"), "Test product")
        if selected == "Custom product"
        else selected
    )

    saved_currency = (
        str(product.get("currency_code") or "").upper()
        if product is not None and "currency_code" in products.columns
        else ""
    )

    default_commission = 120.0
    if product is not None:
        for column in ("commission_amount", "commission"):
            if column in products.columns:
                value = product.get(column)
                if value is not None and not st.session_state.get("ignore_commission"):
                    try:
                        if float(value) > 0:
                            default_commission = float(value)
                            break
                    except (TypeError, ValueError):
                        pass

    currency = st.selectbox(
        "Scenario currency",
        CURRENCIES,
        index=CURRENCIES.index(saved_currency)
        if saved_currency in CURRENCIES else 0,
    )

    with st.form("calc"):
        a, b = st.columns(2)

        budget = a.number_input(
            f"Budget ({currency})",
            min_value=0.0,
            value=500.0,
            step=50.0,
        )

        cpc = a.number_input(
            f"Average CPC ({currency})",
            min_value=0.01,
            value=1.5,
        )

        cr = b.number_input(
            ui("Conversion rate %"),
            min_value=0.0,
            max_value=100.0,
            value=2.0,
        )

        commission = b.number_input(
            f"Commission ({currency})",
            min_value=0.01,
            value=default_commission,
        )

        ok = st.form_submit_button(
            ui("Calculate scenario"),
            use_container_width=True,
        )

    if ok:
        try:
            st.session_state.result = calculate_campaign(
                name,
                budget,
                cpc,
                cr,
                commission,
                currency,
            )
        except ValueError as exc:
            st.error(str(exc))
            st.session_state.pop("result", None)

    result = st.session_state.get("result")

    if not result:
        return

    a, b, c, d = st.columns(4)

    a.metric(ui("Clicks"), f"{result.clicks:,.0f}")
    b.metric(ui("Expected sales"), f"{result.sales:,.2f}")
    c.metric(
        ui("Revenue"),
        format_currency(result.revenue, result.currency_code),
    )
    d.metric(
        ui("Profit"),
        format_currency(result.profit, result.currency_code),
    )

    a, b, c = st.columns(3)

    a.metric(ui("ROAS"), f"{result.roas:.2f}x")
    b.metric(ui("ROI"), f"{result.roi * 100:.2f}%")
    c.metric(
        ui("Break-even conversion"),
        f"{result.break_even_conversion_rate * 100:.2f}%",
    )

    st.caption(ui("Modelled estimates, not guaranteed results."))

    if st.button(ui("Save scenario"), type="primary"):
        insert_record("campaign_scenarios", result.as_record())
        st.success(ui("Scenario saved."))
