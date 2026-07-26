import streamlit as st
NAV={'🏠 Dashboard':'dashboard','📈 Product Research':'product_research','🔍 Keyword Research':'keyword_research','🤖 AI Assistant':'ai_assistant','💰 Profit Calculator':'profit_calculator','📊 Analytics':'analytics','🌐 Landing Pages':'landing_pages','📧 Email Marketing':'email_marketing','📰 SEO':'seo','🎯 Google Ads':'google_ads','🛒 Affiliate Products':'affiliate_products','⚙️ Settings':'settings'}
def sidebar_navigation():
    with st.sidebar:
        st.markdown('<h2>⚡ Filtrify AI</h2><p class="muted">Affiliate Intelligence Platform</p>',unsafe_allow_html=True)
        label=st.radio('Navigation',list(NAV),label_visibility='collapsed'); st.divider(); st.caption('Development build · Month 1 foundation')
    return NAV[label]
def page_header(eyebrow,title,subtitle):
    st.markdown(f'<section class="hero"><div class="eyebrow">{eyebrow}</div><div class="title">{title}</div><div class="subtitle">{subtitle}</div></section>',unsafe_allow_html=True)
