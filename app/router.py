"""Application route configuration for YAffiliate."""

from __future__ import annotations

import streamlit as st

from app.pages import (
    affiliate_products,
    ai_assistant,
    analytics,
    campaign_generator,
    campaign_history,
    content_studio,
    dashboard,
    email_marketing,
    google_ads,
    growth_dashboard,
    keyword_research,
    landing_pages,
    mission_center,
    portfolio_intelligence,
    product_discovery,
    product_intelligence,
    product_research,
    profit_calculator,
    quick_generate,
    seo,
    settings,
)
from app.services.admin_service import AdminService
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import ui


ROUTES = {
    "dashboard": dashboard.render,
    "mission_center": mission_center.render,
    "product_intelligence": product_intelligence.render,
    "portfolio_intelligence": portfolio_intelligence.render,
    "product_research": product_research.render,
    "product_discovery": product_discovery.render,
    "content_studio": content_studio.render,
    "quick_generate": quick_generate.render,
    "campaign_generator": campaign_generator.render,
    "campaign_history": campaign_history.render,
    "keyword_research": keyword_research.render,
    "ai_assistant": ai_assistant.render,
    "profit_calculator": profit_calculator.render,
    "analytics": analytics.render,
    "landing_pages": landing_pages.render,
    "email_marketing": email_marketing.render,
    "seo": seo.render,
    "google_ads": google_ads.render,
    "affiliate_products": affiliate_products.render,
    "settings": settings.render,
    "growth_dashboard": growth_dashboard.render,
}


PRO_ROUTES = {
    "product_intelligence",
    "portfolio_intelligence",
    "product_research",
    "product_discovery",
    "content_studio",
    "campaign_generator",
    "campaign_history",
    "keyword_research",
    "ai_assistant",
    "analytics",
    "landing_pages",
    "email_marketing",
    "seo",
    "google_ads",
    "affiliate_products",
}


ADMIN_ROUTES = {
    "growth_dashboard",
}


def _user_is_pro() -> bool:
    """Return the signed-in user's verified Pro entitlement."""
    user_id = str(
        st.session_state.get("auth_user_id", "") or ""
    ).strip()

    if not user_id:
        return False

    try:
        return SubscriptionService().is_pro(user_id)

    except Exception:
        return False


def _render_pro_paywall() -> None:
    """Render a simple upgrade screen for protected routes."""
    st.title(ui("🔒 YAffiliate Pro"))

    st.subheader(
        ui("This feature is available with YAffiliate Pro.")
    )

    st.write(
        ui(
            "Upgrade to unlock YAffiliate's advanced AI "
            "marketing, research, campaign and analytics tools."
        )
    )

    st.info(
        ui(
            "Open Settings to start a secure Stripe "
            "subscription."
        )
    )

    if st.button(
        ui("💳 View YAffiliate Pro"),
        type="primary",
        use_container_width=True,
    ):
        st.session_state["_pending_route"] = "settings"
        st.rerun()


def _render_admin_denied() -> None:
    """Render a generic response for private owner routes."""
    st.error("This page is not available.")


def render_route(route: str) -> None:
    """Render a route while enforcing access controls."""
    page = ROUTES.get(route)

    if page is None:
        dashboard.render()
        return

    if route in ADMIN_ROUTES:
        if not AdminService.is_admin():
            _render_admin_denied()
            return

    if route in PRO_ROUTES:
        if not _user_is_pro():
            _render_pro_paywall()
            return

    page()