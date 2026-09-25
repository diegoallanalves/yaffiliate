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


# ---------------------------------------------------------
# Navigation groups
# ---------------------------------------------------------
# These groups organize the platform around the customer's
# workflow instead of displaying every feature at once.
NAV_GROUPS = [
    (
        "🚀",
        "nav_start",
        [
            "quick_generate",
            "dashboard",
            "mission_center",
        ],
    ),
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


def _get_nav_item(route: str):
    """Return navigation metadata for a route."""

    for item in NAV_ITEMS:
        if item[2] == route:
            return item

    return None


def _route_label(
    route: str,
    is_pro: bool,
) -> str:
    """Build the customer-facing label for one route."""

    item = _get_nav_item(route)

    if item is None:
        return route

    icon, translation_key, _, requires_pro = item

    name = t(translation_key)

    # Keep the menu visually clean.
    # Only show a Pro badge on locked features.
    if requires_pro and not is_pro:
        suffix = "  🔒"
    elif requires_pro and is_pro:
        suffix = "  ✦"
    else:
        suffix = ""

    return f"{icon} {name}{suffix}"


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
        # customer-facing navigation labels.
        current_route = st.session_state.get(
            "selected_route",
            "quick_generate",
        )

        set_language(selected_language_code)

        st.session_state[
            PENDING_ROUTE_KEY
        ] = current_route

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

    st.session_state[
        PENDING_ROUTE_KEY
    ] = route

    st.rerun()


def _render_group(
    title: str,
    routes: list[str],
    is_pro: bool,
    current_route: str,
) -> str:
    """Render one expandable navigation group."""

    group_contains_current_route = (
        current_route in routes
    )

    selected_route = current_route

    with st.expander(
        title,
        expanded=group_contains_current_route,
    ):

        for route in routes:

            label = _route_label(
                route,
                is_pro,
            )

            is_current = (
                route == current_route
            )

            button_type = (
                "primary"
                if is_current
                else "secondary"
            )

            if st.button(
                label,
                key=f"nav_{route}",
                use_container_width=True,
                type=button_type,
            ):
                selected_route = route

    return selected_route


def sidebar_navigation() -> str:
    """Render the sidebar and return the selected route."""

    is_pro = _is_pro_user()

    # ---------------------------------------------------------
    # Handle navigation requested by another page
    # ---------------------------------------------------------

    pending_route = st.session_state.pop(
        PENDING_ROUTE_KEY,
        None,
    )

    if pending_route is not None:

        valid_routes = {
            item[2]
            for item in NAV_ITEMS
        }

        if pending_route not in valid_routes:
            raise ValueError(
                f"Unknown YAffiliate route: {pending_route}"
            )

        st.session_state[
            "selected_route"
        ] = pending_route

    current_route = st.session_state.get(
        "selected_route",
        "quick_generate",
    )

    valid_routes = {
        item[2]
        for item in NAV_ITEMS
    }

    if current_route not in valid_routes:
        current_route = "quick_generate"

    # ---------------------------------------------------------
    # Sidebar
    # ---------------------------------------------------------

    with st.sidebar:

        # -----------------------------------------------------
        # Branding
        # -----------------------------------------------------

        st.markdown(
            f"""
            <h2>🚀 YAffiliate</h2>
            <p class="muted">{t("platform_tagline")}</p>
            """,
            unsafe_allow_html=True,
        )

        # -----------------------------------------------------
        # Language
        # -----------------------------------------------------

        _render_language_selector()

        st.divider()

        # -----------------------------------------------------
        # Main navigation
        # -----------------------------------------------------

        selected_route = current_route

        for (
            group_icon,
            group_translation_key,
            group_routes,
        ) in NAV_GROUPS:

            group_title = f"{group_icon} {t(group_translation_key)}"

            group_selection = _render_group(
                title=group_title,
                routes=group_routes,
                is_pro=is_pro,
                current_route=selected_route,
            )

            if group_selection != selected_route:
                selected_route = group_selection
                st.session_state[
                    "selected_route"
                ] = selected_route
                st.rerun()

        # -----------------------------------------------------
        # Settings
        # -----------------------------------------------------

        st.divider()

        settings_label = _route_label(
            "settings",
            is_pro,
        )

        if st.button(
            settings_label,
            key="nav_settings",
            use_container_width=True,
            type=(
                "primary"
                if selected_route == "settings"
                else "secondary"
            ),
        ):
            selected_route = "settings"

            st.session_state[
                "selected_route"
            ] = selected_route

            st.rerun()

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
