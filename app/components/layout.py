"""Shared YAffiliate navigation and page-header components."""

from __future__ import annotations

import streamlit as st

from app.services.subscription_service import SubscriptionService


# Keep route definitions separate from customer-facing labels.
# The router remains responsible for enforcing Pro access.
NAV_ITEMS = [
    ("🚀", "Quick Generate", "quick_generate", False),
    ("🏠", "Dashboard", "dashboard", False),
    ("🎯", "Mission Center", "mission_center", False),
    ("🧠", "Product Intelligence", "product_intelligence", True),
    ("📊", "Portfolio Intelligence", "portfolio_intelligence", True),
    ("📈", "Product Research", "product_research", True),
    ("⭐", "Product Discovery", "product_discovery", True),
    ("✍️", "AI Content Studio", "content_studio", True),
    ("🚀", "Campaign Generator", "campaign_generator", True),
    ("🕘", "Campaign History", "campaign_history", True),
    ("🔍", "Keyword Research", "keyword_research", True),
    ("🤖", "AI Assistant", "ai_assistant", True),
    ("💰", "Profit Calculator", "profit_calculator", False),
    ("📊", "Analytics", "analytics", True),
    ("🌐", "Landing Pages", "landing_pages", True),
    ("📧", "Email Marketing", "email_marketing", True),
    ("📰", "SEO", "seo", True),
    ("🎯", "Google Ads", "google_ads", True),
    ("🛒", "Affiliate Products", "affiliate_products", True),
    ("⚙️", "Settings", "settings", False),
]

NAV_WIDGET_KEY = "yaffiliate_navigation"
PENDING_ROUTE_KEY = "_pending_route"


def _is_pro_user() -> bool:
    """Return True when the signed-in user has an active Pro subscription."""
    user_id = str(st.session_state.get("auth_user_id", "") or "").strip()

    if not user_id:
        return False

    try:
        return SubscriptionService().is_pro(user_id)
    except Exception:
        # Navigation display must never break the application.
        # router.py still independently enforces Pro access.
        return False


def _build_navigation(is_pro: bool) -> tuple[dict[str, str], dict[str, str]]:
    """Build labels for the current subscription while preserving routes."""
    nav: dict[str, str] = {}
    route_to_label: dict[str, str] = {}

    for icon, name, route, requires_pro in NAV_ITEMS:
        if requires_pro:
            suffix = " · PRO ✓" if is_pro else " · PRO 🔒"
        else:
            suffix = ""

        label = f"{icon} {name}{suffix}"
        nav[label] = route
        route_to_label[route] = label

    return nav, route_to_label


def navigate_to(route: str) -> None:
    """Navigate to another YAffiliate page on the next rerun."""
    valid_routes = {item[2] for item in NAV_ITEMS}

    if route not in valid_routes:
        raise ValueError(f"Unknown YAffiliate route: {route}")

    st.session_state[PENDING_ROUTE_KEY] = route
    st.rerun()


def sidebar_navigation() -> str:
    """Render the sidebar and return the selected route."""
    is_pro = _is_pro_user()
    nav, route_to_label = _build_navigation(is_pro)

    pending_route = st.session_state.pop(PENDING_ROUTE_KEY, None)

    if pending_route is not None:
        if pending_route not in route_to_label:
            raise ValueError(
                f"Unknown YAffiliate route: {pending_route}"
            )
        st.session_state[NAV_WIDGET_KEY] = route_to_label[pending_route]

    current_label = st.session_state.get(NAV_WIDGET_KEY)

    # Subscription changes alter the displayed labels. Preserve the selected
    # route when possible instead of resetting the customer unexpectedly.
    if current_label not in nav:
        selected_route = st.session_state.get(
            "selected_route",
            "quick_generate",
        )
        st.session_state[NAV_WIDGET_KEY] = route_to_label.get(
            selected_route,
            route_to_label["quick_generate"],
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
            options=list(nav.keys()),
            key=NAV_WIDGET_KEY,
            label_visibility="collapsed",
        )

        st.divider()

        if is_pro:
            st.caption("✓ YAffiliate Pro active")
        else:
            st.caption("🔒 PRO features require an active subscription.")

        st.caption(
            "YAffiliate Beta · Build your marketing kit in minutes"
        )

    selected_route = nav[selected_label]
    st.session_state["selected_route"] = selected_route

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
