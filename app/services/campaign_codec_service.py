"""Convert saved campaign dictionaries back into CampaignPackage objects."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.models.email_sequence import CampaignEmail, EmailSequence
from app.models.google_ads_campaign import GoogleAdsAsset
from app.models.landing_page import LandingPage, LandingPageSection
from app.models.seo_article import SEOArticle, SEOSection
from app.services.campaign_generator_service import CampaignPackage


def campaign_from_dict(data: dict[str, Any]) -> CampaignPackage:
    """Rebuild a CampaignPackage previously saved as JSON."""
    created_at = _parse_datetime(data.get("created_at"))

    article_data = data["seo_article"]
    landing_data = data["landing_page"]
    email_data = data["email_sequence"]
    ads_data = data["google_ads"]

    article = SEOArticle(
        title=article_data["title"],
        meta_description=article_data["meta_description"],
        target_keyword=article_data["target_keyword"],
        introduction=article_data["introduction"],
        sections=[SEOSection(**item) for item in article_data.get("sections", [])],
        conclusion=article_data.get("conclusion", ""),
        call_to_action=article_data.get("call_to_action", ""),
        estimated_word_count=int(article_data.get("estimated_word_count", 0)),
        seo_score=float(article_data.get("seo_score", 0.0)),
    )

    landing_page = LandingPage(
        page_title=landing_data["page_title"],
        meta_description=landing_data["meta_description"],
        product_name=landing_data["product_name"],
        target_audience=landing_data["target_audience"],
        primary_goal=landing_data["primary_goal"],
        tone=landing_data["tone"],
        hero_headline=landing_data["hero_headline"],
        hero_subheadline=landing_data["hero_subheadline"],
        primary_cta=landing_data["primary_cta"],
        sections=[LandingPageSection(**item) for item in landing_data.get("sections", [])],
        final_cta_heading=landing_data.get("final_cta_heading", ""),
        final_cta_text=landing_data.get("final_cta_text", ""),
        final_cta_button=landing_data.get("final_cta_button", ""),
        estimated_word_count=int(landing_data.get("estimated_word_count", 0)),
        conversion_score=float(landing_data.get("conversion_score", 0.0)),
    )

    email_sequence = EmailSequence(
        sequence_name=email_data["sequence_name"],
        product_name=email_data["product_name"],
        target_audience=email_data["target_audience"],
        tone=email_data["tone"],
        emails=tuple(CampaignEmail(**item) for item in email_data.get("emails", [])),
        strategy_summary=email_data.get("strategy_summary", ""),
        primary_goal=email_data.get("primary_goal", "Visit Sales Page"),
    )

    google_ads = GoogleAdsAsset(
        campaign_name=ads_data["campaign_name"],
        headlines=tuple(ads_data.get("headlines", [])),
        descriptions=tuple(ads_data.get("descriptions", [])),
        keywords=tuple(ads_data.get("keywords", [])),
        negative_keywords=tuple(ads_data.get("negative_keywords", [])),
        call_to_action=ads_data.get("call_to_action", ""),
        target_audience=ads_data.get("target_audience", ""),
    )

    return CampaignPackage(
        campaign_name=data["campaign_name"],
        product_name=data["product_name"],
        seo_article=article,
        landing_page=landing_page,
        email_sequence=email_sequence,
        google_ads=google_ads,
        target_keyword=data.get("target_keyword", ""),
        target_audience=data.get("target_audience", ""),
        tone=data.get("tone", "Professional"),
        created_at=created_at,
    )


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)
