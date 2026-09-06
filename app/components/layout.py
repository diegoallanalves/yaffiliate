"""Shared YAffiliate navigation and page-header components."""

from __future__ import annotations

import streamlit as st

from app.services.subscription_service import SubscriptionService
from app.services.translation_service import (
    LANGUAGES,
    get_language,
    get_language_name,
    set_language,
    t,
    translate_literal,
)


# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------
# Structure:
# (icon, translation_key, route, requires_pro)
#
# IMPORTANT:
# Routes never change when the language changes.
# Only the customer-facing labels are translated.
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
]


NAV_WIDGET_KEY = "yaffiliate_navigation"
PENDING_ROUTE_KEY = "_pending_route"
LANGUAGE_WIDGET_KEY = "yaffiliate_language_selector"


def _is_pro_user() -> bool:
    """Return True when the signed-in user currently has Pro access."""

    user_id = str(
        st.session_state.get("auth_user_id", "") or ""
    ).strip()

    if not user_id:
        return False

    try:
        return SubscriptionService().is_pro(user_id)

    except Exception:
        # Navigation must never break the application.
        # router.py independently enforces Pro access.
        return False


def _build_navigation(
    is_pro: bool,
) -> tuple[dict[str, str], dict[str, str]]:
    """Build translated navigation labels while preserving routes."""

    nav: dict[str, str] = {}
    route_to_label: dict[str, str] = {}

    for icon, translation_key, route, requires_pro in NAV_ITEMS:

        name = t(translation_key)

        if requires_pro:
            suffix = " · PRO ✓" if is_pro else " · PRO 🔒"
        else:
            suffix = ""

        label = f"{icon} {name}{suffix}"

        nav[label] = route
        route_to_label[route] = label

    return nav, route_to_label


def _render_language_selector() -> None:
    """Render and process the YAffiliate language selector."""

    current_language_name = get_language_name()

    language_names = list(LANGUAGES.keys())

    if current_language_name not in language_names:
        current_language_name = "English"

    current_index = language_names.index(
        current_language_name
    )

    selected_language_name = st.selectbox(
        f"🌐 {t('language')}",
        options=language_names,
        index=current_index,
        key=LANGUAGE_WIDGET_KEY,
    )

    selected_language_code = LANGUAGES[
        selected_language_name
    ]

    if selected_language_code != get_language():

        # Preserve the current route before translating
        # all customer-facing navigation labels.
        current_route = st.session_state.get(
            "selected_route",
            "quick_generate",
        )

        set_language(selected_language_code)

        st.session_state[PENDING_ROUTE_KEY] = current_route

        # The radio widget contains translated text, so its old
        # value must be removed before rebuilding the navigation.
        st.session_state.pop(
            NAV_WIDGET_KEY,
            None,
        )

        st.rerun()


def navigate_to(route: str) -> None:
    """Navigate to another YAffiliate page on the next rerun."""

    valid_routes = {
        item[2]
        for item in NAV_ITEMS
    }

    if route not in valid_routes:
        raise ValueError(
            f"Unknown YAffiliate route: {route}"
        )

    st.session_state[PENDING_ROUTE_KEY] = route

    st.rerun()


def sidebar_navigation() -> str:
    """Render the sidebar and return the selected route."""

    is_pro = _is_pro_user()

    # ---------------------------------------------------------
    # Sidebar branding + language
    # ---------------------------------------------------------
    with st.sidebar:

        st.markdown(
            f"""
            <h2>🚀 YAffiliate</h2>
            <p class="muted">{t("platform_tagline")}</p>
            """,
            unsafe_allow_html=True,
        )

        _render_language_selector()

        st.divider()

    # ---------------------------------------------------------
    # Build translated navigation AFTER language selection
    # ---------------------------------------------------------
    nav, route_to_label = _build_navigation(
        is_pro
    )

    pending_route = st.session_state.pop(
        PENDING_ROUTE_KEY,
        None,
    )

    if pending_route is not None:

        if pending_route not in route_to_label:
            raise ValueError(
                f"Unknown YAffiliate route: {pending_route}"
            )

        st.session_state[
            NAV_WIDGET_KEY
        ] = route_to_label[pending_route]

    current_label = st.session_state.get(
        NAV_WIDGET_KEY
    )

    # Language or subscription changes can alter the
    # customer-facing label. Preserve the underlying route.
    if current_label not in nav:

        selected_route = st.session_state.get(
            "selected_route",
            "quick_generate",
        )

        st.session_state[
            NAV_WIDGET_KEY
        ] = route_to_label.get(
            selected_route,
            route_to_label["quick_generate"],
        )

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------
    with st.sidebar:

        selected_label = st.radio(
            t("navigation"),
            options=list(nav.keys()),
            key=NAV_WIDGET_KEY,
            label_visibility="collapsed",
        )

        st.divider()

        # -----------------------------------------------------
        # Subscription status
        # -----------------------------------------------------
        if is_pro:

            st.caption(
                f"✓ {t('pro_active')}"
            )

        else:

            st.caption(
                f"🔒 {t('pro_required')}"
            )

        # -----------------------------------------------------
        # Beta branding
        # -----------------------------------------------------
        st.caption(
            t("beta_tagline")
        )

    selected_route = nav[selected_label]

    st.session_state[
        "selected_route"
    ] = selected_route

    return selected_route


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
) -> None:
    """Render the shared page header."""

    eyebrow = translate_literal(eyebrow)
    title = translate_literal(title)
    subtitle = translate_literal(subtitle)

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