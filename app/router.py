from app.pages import (
    dashboard,
    mission_center,
    product_intelligence,
    portfolio_intelligence,
    product_research,
    product_discovery,
    content_studio,
    keyword_research,
    ai_assistant,
    profit_calculator,
    analytics,
    landing_pages,
    email_marketing,
    seo,
    google_ads,
    affiliate_products,
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


def render_route(route: str) -> None:
    page = ROUTES.get(route)

    if page is None:
        dashboard.render()
        return

    page()