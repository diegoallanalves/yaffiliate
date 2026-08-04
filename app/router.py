"""Application route configuration for Filtrify."""

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
    keyword_research,
    landing_pages,
    mission_center,
    portfolio_intelligence,
    product_discovery,
    product_intelligence,
    product_research,
    profit_calculator,
    seo,
    settings,
)


ROUTES = {
    "dashboard": dashboard.render,
    "mission_center": mission_center.render,
    "product_intelligence": product_intelligence.render,
    "portfolio_intelligence": portfolio_intelligence.render,
    "product_research": product_research.render,
    "product_discovery": product_discovery.render,
    "content_studio": content_studio.render,
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
}


def render_route(
    route: str,
) -> None:
    """Render the page associated with the selected route.

    When the route is unknown, Filtrify falls back to the dashboard.
    """

    page = ROUTES.get(
        route
    )

    if page is None:
        dashboard.render()
        return

    page()