"""Shared YAffiliate navigation and page-header components."""

from __future__ import annotations

import streamlit as st


NAV = {
    "🚀 Quick Generate": "quick_generate",
    "🏠 Dashboard": "dashboard",
    "🎯 Mission Center": "mission_center",
    "🧠 Product Intelligence": "product_intelligence",
    "📊 Portfolio Intelligence": "portfolio_intelligence",
    "📈 Product Research": "product_research",
    "⭐ Product Discovery": "product_discovery",
    "✍️ AI Content Studio": "content_studio",
    "🚀 Campaign Generator": "campaign_generator",
    "🕘 Campaign History": "campaign_history",
    "🔍 Keyword Research": "keyword_research",
    "🤖 AI Assistant": "ai_assistant",
    "💰 Profit Calculator": "profit_calculator",
    "📊 Analytics": "analytics",
    "🌐 Landing Pages": "landing_pages",
    "📧 Email Marketing": "email_marketing",
    "📰 SEO": "seo",
    "🎯 Google Ads": "google_ads",
    "🛒 Affiliate Products": "affiliate_products",
    "⚙️ Settings": "settings",
}

ROUTE_TO_LABEL = {
    route: label
    for label, route in NAV.items()
}

NAV_WIDGET_KEY = "yaffiliate_navigation"
PENDING_ROUTE_KEY = "_pending_route"


def navigate_to(route: str) -> None:
    """Navigate to another YAffiliate page on the next rerun."""

    if route not in ROUTE_TO_LABEL:
        raise ValueError(
            f"Unknown YAffiliate route: {route}"
        )

    st.session_state[PENDING_ROUTE_KEY] = route
    st.rerun()


def sidebar_navigation() -> str:
    """Render the sidebar and return the selected route."""

    pending_route = st.session_state.pop(
        PENDING_ROUTE_KEY,
        None,
    )

    if pending_route is not None:
        if pending_route not in ROUTE_TO_LABEL:
            raise ValueError(
                f"Unknown YAffiliate route: {pending_route}"
            )

        # Important:
        # Set the radio widget value BEFORE creating the widget.
        st.session_state[NAV_WIDGET_KEY] = (
            ROUTE_TO_LABEL[pending_route]
        )

    if NAV_WIDGET_KEY not in st.session_state:
        st.session_state[NAV_WIDGET_KEY] = (
            "🚀 Quick Generate"
        )

    with st.sidebar:
        st.markdown(
            """
            <h2>🚀 YAffiliate</h2>
            <p class="muted">AI Marketing Platform</p>
            """,
            unsafe_allow_html=True,
        )

        selected_label = st.radio(
            "Navigation",
            options=list(NAV.keys()),
            key=NAV_WIDGET_KEY,
            label_visibility="collapsed",
        )

        st.divider()

        st.caption(
            "YAffiliate Beta · Build your marketing kit in minutes"
        )

    selected_route = NAV[selected_label]

    st.session_state["selected_route"] = (
        selected_route
    )

    return selected_route


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
) -> None:
    """Render the shared page header."""

    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <div class="title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
