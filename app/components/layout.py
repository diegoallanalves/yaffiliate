import streamlit as st

NAV = {
    "🏠 Dashboard": "dashboard",
    "🎯 Mission Center": "mission_center",
    "🧠 Product Intelligence": "product_intelligence",
    "📊 Portfolio Intelligence": "portfolio_intelligence",
    "📈 Product Research": "product_research",
    "⭐ Product Discovery": "product_discovery",
    "✍️ AI Content Studio": "content_studio",
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


def sidebar_navigation():
    with st.sidebar:
        st.markdown(
            '''
            <h2>⚡ Filtrify AI</h2>
            <p class="muted">Affiliate Intelligence Platform</p>
            ''',
            unsafe_allow_html=True,
        )

        label = st.radio(
            'Navigation',
            list(NAV),
            label_visibility='collapsed'
        )

        st.divider()

        st.caption(
            'Development build · Milestone 3 — Product Intelligence'
        )

    return NAV[label]


def page_header(
    eyebrow,
    title,
    subtitle,
):
    st.markdown(
        f'''
        <section class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <div class="title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </section>
        ''',
        unsafe_allow_html=True,
    )