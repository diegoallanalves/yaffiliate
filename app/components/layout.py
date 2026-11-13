
"""Shared YAffiliate navigation and page headers."""

from __future__ import annotations

from html import escape

import streamlit as st

from app.services.admin_service import AdminService
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import (
    LANGUAGES,
    get_language,
    get_language_name,
    set_language,
    t,
    translate_literal,
)


NAV_ITEMS = [
    ("🚀", "quick_generate", "quick_generate", False),
    ("🏠", "dashboard", "dashboard", False),
    ("🎯", "mission_center", "mission_center", False),
    ("🧠", "product_intelligence", "product_intelligence", True),
    ("📊", "portfolio_intelligence", "portfolio_intelligence", True),
    ("📈", "product_research", "product_research", True),
    ("⭐", "product_discovery", "product_discovery", True),
    ("✍️", "content_studio", "content_studio", True),
    ("🚀", "campaign_generator", "campaign_generator", True),
    ("🕘", "campaign_history", "campaign_history", True),
    ("🔍", "keyword_research", "keyword_research", True),
    ("🤖", "ai_assistant", "ai_assistant", True),
    ("💰", "profit_calculator", "profit_calculator", False),
    ("📊", "analytics", "analytics", True),
    ("🌐", "landing_pages", "landing_pages", True),
    ("📧", "email_marketing", "email_marketing", True),
    ("📰", "seo", "seo", True),
    ("🎯", "google_ads", "google_ads", True),
    ("🛒", "affiliate_products", "affiliate_products", True),
    ("⚙️", "settings", "settings", False),
    ("📈", "growth_dashboard", "growth_dashboard", False),
]

NAV_GROUPS = [
    (
        "🔎",
        "nav_research",
        [
            "product_discovery",
            "product_research",
            "product_intelligence",
            "keyword_research",
        ],
    ),
    (
        "✨",
        "nav_create",
        [
            "content_studio",
            "campaign_generator",
            "campaign_history",
            "landing_pages",
            "email_marketing",
            "seo",
            "google_ads",
        ],
    ),
    (
        "📊",
        "nav_optimize",
        [
            "portfolio_intelligence",
            "profit_calculator",
            "analytics",
        ],
    ),
    (
        "🤖",
        "nav_ai_products",
        [
            "ai_assistant",
            "affiliate_products",
        ],
    ),
]

PENDING_ROUTE_KEY = "_pending_route"
LANGUAGE_WIDGET_KEY = "yaffiliate_language_selector"
VALID_ROUTES = {item[2] for item in NAV_ITEMS}


def _is_pro_user() -> bool:
    user_id = str(
        st.session_state.get("auth_user_id") or ""
    ).strip()

    if not user_id:
        return False

    try:
        return bool(SubscriptionService().is_pro(user_id))
    except Exception:
        return False


def _route_label(route: str, is_pro: bool) -> str:
    item = next(
        (item for item in NAV_ITEMS if item[2] == route),
        None,
    )

    if item is None:
        return route

    icon, translation_key, _, requires_pro = item
    label = t(translation_key)

    if requires_pro and not is_pro:
        label += " 🔒"

    return f"{icon} {label}"


def _render_language_selector() -> None:
    language_names = list(LANGUAGES.keys())
    current_name = get_language_name()

    if current_name not in language_names:
        current_name = "English"

    selected = st.selectbox(
        f"🌐 {t('language')}",
        options=language_names,
        index=language_names.index(current_name),
        key=LANGUAGE_WIDGET_KEY,
    )

    selected_code = LANGUAGES[selected]

    if selected_code != get_language():
        current_route = st.session_state.get(
            "selected_route",
            "dashboard",
        )

        set_language(selected_code)
        st.session_state[PENDING_ROUTE_KEY] = current_route
        st.rerun()


def navigate_to(route: str) -> None:
    if route not in VALID_ROUTES:
        raise ValueError(f"Unknown YAffiliate route: {route}")

    st.session_state[PENDING_ROUTE_KEY] = route
    st.rerun()


def _nav_button(route: str, is_pro: bool, current: str) -> None:
    if st.button(
        _route_label(route, is_pro),
        key=f"nav_{route}",
        type="primary" if route == current else "secondary",
        use_container_width=True,
    ):
        st.session_state["selected_route"] = route
        st.rerun()


def sidebar_navigation() -> str:
    """Compact navigation with three main destinations."""

    pending = st.session_state.pop(PENDING_ROUTE_KEY, None)

    if pending is not None:
        if pending not in VALID_ROUTES:
            raise ValueError(f"Unknown YAffiliate route: {pending}")
        st.session_state["selected_route"] = pending

    current = st.session_state.get("selected_route", "dashboard")

    if current not in VALID_ROUTES:
        current = "dashboard"

    is_pro = _is_pro_user()

    with st.sidebar:
        st.markdown("### 🚀 YAffiliate")
        st.caption(t("platform_tagline"))

        _render_language_selector()

        st.divider()

        # Main destinations
        _nav_button("dashboard", is_pro, current)
        _nav_button("quick_generate", is_pro, current)
        _nav_button("mission_center", is_pro, current)

        st.divider()

        # Advanced features remain accessible but collapsed.
        for icon, translation_key, routes in NAV_GROUPS:
            with st.expander(
                f"{icon} {t(translation_key)}",
                expanded=current in routes,
            ):
                for route in routes:
                    _nav_button(route, is_pro, current)

        st.divider()

        _nav_button("settings", is_pro, current)

        if AdminService.is_admin():
            with st.expander("🔧 Owner tools", expanded=current == "growth_dashboard"):
                _nav_button("growth_dashboard", is_pro, current)

        st.divider()

        if is_pro:
            st.caption(f"✓ {t('pro_active')}")
        else:
            st.caption(f"🔒 {t('pro_required')}")

        st.caption(t("beta_tagline"))

    st.session_state["selected_route"] = current
    return current


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
) -> None:
    """Render the shared page header."""

    eyebrow = escape(str(translate_literal(eyebrow)))
    title = escape(str(translate_literal(title)))
    subtitle = escape(str(translate_literal(subtitle)))

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
