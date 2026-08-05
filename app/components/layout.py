"""Shared Filtrify navigation and page-header components."""

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


def sidebar_navigation() -> str:
    """Render the Filtrify sidebar and return the selected route key."""

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
            label_visibility="collapsed",
        )

        st.divider()

        st.caption(
            "YAffiliate Beta · Build your marketing kit in minutes"
        )

    return NAV[selected_label]


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
) -> None:
    """Render the shared Filtrify page header."""

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