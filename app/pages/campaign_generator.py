"""Campaign Generator page for YAffiliate."""

from __future__ import annotations

import re
import streamlit as st

from app.collectors.hotmart_collector import HotmartCollector
from app.components.layout import navigate_to, page_header
from app.models.email_sequence import EmailSequence
from app.models.google_ads_campaign import GoogleAdsAsset
from app.models.landing_page import LandingPage
from app.models.seo_article import SEOArticle
from app.repositories.campaign_repository import CampaignRepository
from app.services.campaign_export_service import CampaignExportService
from app.services.campaign_codec_service import campaign_from_dict
from app.services.campaign_generator_service import (
    CampaignGeneratorService,
    CampaignPackage,
)
from app.services.comparison_service import ComparisonService
from app.services.exports import ZipExporter
from app.services.product_analysis_service import ProductAnalysisService


collector = HotmartCollector()
comparison_service = ComparisonService()
analysis_service = ProductAnalysisService()
campaign_service = CampaignGeneratorService()
campaign_export_service = CampaignExportService()
campaign_repository = CampaignRepository()
zip_exporter = ZipExporter()


def render() -> None:
    """Render the YAffiliate Campaign Generator page."""

    loaded_campaign = st.session_state.get("loaded_campaign")

    if isinstance(loaded_campaign, dict) and not isinstance(
        st.session_state.get("generated_campaign"), CampaignPackage
    ):
        try:
            st.session_state["generated_campaign"] = campaign_from_dict(loaded_campaign)
        except Exception as error:
            st.warning("The saved campaign settings were loaded, but its assets could not be reconstructed.")
            st.caption(str(error))

    loaded_product_name = ""
    loaded_target_keyword = ""
    loaded_target_audience = ""
    loaded_campaign_name = ""
    loaded_tone = "Professional"

    if isinstance(loaded_campaign, dict):
        loaded_product_name = str(
            loaded_campaign.get("product_name", "")
        ).strip()
        loaded_target_keyword = str(
            loaded_campaign.get("target_keyword", "")
        ).strip()
        loaded_target_audience = str(
            loaded_campaign.get("target_audience", "")
        ).strip()
        loaded_campaign_name = str(
            loaded_campaign.get("campaign_name", "")
        ).strip()
        loaded_tone = str(
            loaded_campaign.get("tone", "Professional")
        ).strip() or "Professional"

        st.success("Saved campaign loaded from Campaign History.")

        if st.button(
            "← Back to Campaign History",
            key="back_to_campaign_history",
        ):
            navigate_to("campaign_history")
            st.rerun()

        if st.button(
            "Clear loaded campaign",
            type="secondary",
            key="clear_loaded_campaign",
        ):
            st.session_state.pop("loaded_campaign", None)
            st.session_state.pop("loaded_campaign_id", None)
            st.session_state.pop("generated_campaign", None)
            st.rerun()

    page_header(
        "Campaign Generator",
        "Create coordinated marketing assets from one product.",
        (
            "Generate an SEO article, landing page, email sequence, "
            "and Google Ads campaign using the same product intelligence, "
            "audience, tone, and campaign goal."
        ),
    )

    search_keyword = loaded_product_name or "Excel"

    products = collector.search_products(
        keyword=search_keyword,
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    if not products and loaded_product_name:
        products = collector.search_products(
            keyword="Excel",
            country_code="BR",
            language_code="pt-BR",
            limit=10,
        )

    if not products:
        st.info("No products are currently available for campaign generation.")
        return

    product_options = {
        index: product.product_name
        for index, product in enumerate(products)
    }

    default_product_index = 0

    if loaded_product_name:
        for index, product in enumerate(products):
            if product.product_name.strip().lower() == loaded_product_name.lower():
                default_product_index = index
                break

    selected_product_index = st.selectbox(
        "Select a product",
        options=list(product_options.keys()),
        index=default_product_index,
        format_func=lambda index: product_options[index],
        key="campaign_selected_product",
    )

    selected_product = products[selected_product_index]

    default_keyword = (
        loaded_target_keyword
        or selected_product.product_name.replace("Masterclass", "course").strip()
    )

    default_audience = (
        loaded_target_audience
        or "People who want to learn Excel and improve their spreadsheet skills"
    )

    default_campaign_name = (
        loaded_campaign_name
        or f"{selected_product.product_name} Affiliate Campaign"
    )

    tone_options = [
        "Professional",
        "Friendly",
        "Persuasive",
        "Educational",
    ]

    tone_index = (
        tone_options.index(loaded_tone)
        if loaded_tone in tone_options
        else 0
    )

    form_column_1, form_column_2 = st.columns(2)

    with form_column_1:
        target_keyword = st.text_input(
            "Target keyword",
            value=default_keyword,
            placeholder="Excel course",
            key="campaign_target_keyword",
        )

        target_audience = st.text_area(
            "Target audience",
            value=default_audience,
            placeholder="Describe the audience this campaign should target",
            height=110,
            key="campaign_target_audience",
        )

        campaign_name = st.text_input(
            "Campaign name",
            value=default_campaign_name,
            key="campaign_name",
        )

    with form_column_2:
        tone = st.selectbox(
            "Writing tone",
            options=tone_options,
            index=tone_index,
            key="campaign_tone",
        )

        article_length = st.selectbox(
            "SEO article length",
            options=["Short", "Medium", "Long"],
            index=1,
            key="campaign_article_length",
        )

        primary_goal = st.selectbox(
            "Campaign goal",
            options=[
                "Visit Sales Page",
                "Generate Leads",
                "Promote Product",
            ],
            index=0,
            key="campaign_primary_goal",
        )

        email_count = st.selectbox(
            "Email sequence length",
            options=[3, 4, 5],
            index=0,
            format_func=lambda value: f"{value} emails",
            key="campaign_email_count",
        )

    generate_campaign = st.button(
        "🚀 Generate Campaign",
        type="primary",
        width="stretch",
        key="generate_campaign_button",
    )

    if generate_campaign:
        missing_fields = _validate_campaign_fields(
            target_keyword=target_keyword,
            target_audience=target_audience,
            campaign_name=campaign_name,
        )

        if missing_fields:
            st.error(
                "Complete the following fields: "
                + ", ".join(missing_fields)
            )
            return

        try:
            with st.spinner(
                "Analysing the product and generating the campaign..."
            ):
                comparison = comparison_service.compare(products)

                selected_comparison = next(
                    (
                        item
                        for item in comparison.products
                        if item.product.product_name == selected_product.product_name
                    ),
                    None,
                )

                analysis = analysis_service.analyse(
                    product=selected_product,
                    comparison=selected_comparison,
                )

                campaign = campaign_service.generate(
                    product=selected_product,
                    analysis=analysis,
                    target_keyword=target_keyword.strip(),
                    target_audience=target_audience.strip(),
                    tone=tone,
                    article_length=article_length,
                    primary_goal=primary_goal,
                    email_count=email_count,
                    campaign_name=campaign_name.strip(),
                )

            campaign_json = campaign_export_service.to_json(
                campaign
            )

            saved_response = campaign_repository.save_campaign(
                user_id="beta-test-user",
                product_name=campaign.product_name,
                campaign=campaign_json,
            )

            saved_campaign_id = (
                saved_response.data[0]["id"]
                if getattr(saved_response, "data", None)
                else None
            )

            st.session_state["generated_campaign"] = campaign
            st.session_state["generated_campaign_id"] = saved_campaign_id

            # A newly generated campaign is a new working copy.
            st.session_state.pop("loaded_campaign", None)
            st.session_state.pop("loaded_campaign_id", None)

            st.success(
                "Campaign generated and saved to Campaign History."
            )
            st.rerun()

        except Exception as error:
            st.exception(error)
            return

    campaign = st.session_state.get("generated_campaign")

    if not isinstance(campaign, CampaignPackage):
        st.info(
            "Choose a product and generate a campaign "
            "to view the campaign assets."
        )
        return

    _render_campaign_summary(campaign)
    _render_campaign_assets(campaign)
    _render_campaign_export(campaign)


def _render_campaign_summary(campaign: CampaignPackage) -> None:
    st.divider()
    st.subheader(campaign.campaign_name)
    st.caption(f"Product: {campaign.product_name}")

    saved_campaign_id = st.session_state.get(
        "generated_campaign_id"
    )

    if saved_campaign_id:
        st.caption(
            f"Saved Campaign ID: {saved_campaign_id}"
        )

    m1, m2, m3 = st.columns(3)
    m1.metric("Campaign assets", campaign.asset_count)
    m2.metric("Estimated words", f"{campaign.total_estimated_words:,}")
    m3.metric("Average quality", f"{campaign.average_quality_score:.1f}/100")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Target keyword**")
        st.write(campaign.target_keyword)
        st.markdown("**Writing tone**")
        st.write(campaign.tone)

    with c2:
        st.markdown("**Target audience**")
        st.write(campaign.target_audience)
        st.markdown("**Created**")
        st.write(campaign.created_at.strftime("%d %B %Y, %H:%M UTC"))


def _render_campaign_assets(campaign: CampaignPackage) -> None:
    st.divider()

    article_tab, landing_page_tab, email_sequence_tab, google_ads_tab = st.tabs(
        [
            "📰 SEO Article",
            "🌐 Landing Page",
            "📧 Email Sequence",
            "🎯 Google Ads",
        ]
    )

    with article_tab:
        _render_seo_article(campaign.seo_article)

    with landing_page_tab:
        _render_landing_page(campaign.landing_page)

    with email_sequence_tab:
        _render_email_sequence(campaign.email_sequence)

    with google_ads_tab:
        _render_google_ads(campaign.google_ads)


def _render_seo_article(article: SEOArticle) -> None:
    st.subheader(article.title)

    m1, m2 = st.columns(2)
    m1.metric("SEO score", f"{article.seo_score:.1f}/100")
    m2.metric("Estimated words", f"{article.estimated_word_count:,}")

    article_text = _build_article_text(article)

    st.text_area(
        "SEO article content",
        value=article_text,
        height=520,
        key="campaign_seo_article_preview",
    )

    st.download_button(
        label="Download SEO article as TXT",
        data=article_text,
        file_name="yaffiliate_campaign_seo_article.txt",
        mime="text/plain",
        width="stretch",
        key="download_campaign_article",
    )


def _render_landing_page(landing_page: LandingPage) -> None:
    st.subheader(landing_page.page_title)

    m1, m2 = st.columns(2)
    m1.metric("Conversion score", f"{landing_page.conversion_score:.1f}/100")
    m2.metric("Estimated words", f"{landing_page.estimated_word_count:,}")

    landing_page_text = _build_landing_page_text(landing_page)

    st.text_area(
        "Landing-page content",
        value=landing_page_text,
        height=520,
        key="campaign_landing_page_preview",
    )

    st.download_button(
        label="Download landing page as TXT",
        data=landing_page_text,
        file_name="yaffiliate_campaign_landing_page.txt",
        mime="text/plain",
        width="stretch",
        key="download_campaign_landing_page",
    )


def _render_email_sequence(email_sequence: EmailSequence) -> None:
    st.subheader(email_sequence.sequence_name)

    m1, m2 = st.columns(2)
    m1.metric("Emails", email_sequence.email_count)
    m2.metric("Estimated words", f"{email_sequence.total_estimated_words:,}")

    if email_sequence.strategy_summary:
        st.markdown("### Strategy Summary")
        st.write(email_sequence.strategy_summary)

    st.markdown("### Campaign Emails")

    for email in email_sequence.emails:
        with st.expander(
            f"Email {email.sequence_number}: {email.purpose}",
            expanded=(email.sequence_number == 1),
        ):
            st.markdown("**Subject**")
            st.write(email.subject)
            st.markdown("**Preview text**")
            st.write(email.preview_text)
            st.markdown("**Email body**")
            st.write(email.body)
            st.markdown("**Call to Action**")
            st.write(email.call_to_action)

    email_sequence_text = email_sequence.to_plain_text()

    st.download_button(
        label="Download email sequence as TXT",
        data=email_sequence_text,
        file_name="yaffiliate_campaign_email_sequence.txt",
        mime="text/plain",
        width="stretch",
        key="download_campaign_email_sequence",
    )


def _render_google_ads(google_ads: GoogleAdsAsset) -> None:
    st.subheader(google_ads.campaign_name)

    h, d, k = st.columns(3)
    h.metric("Headlines", google_ads.headline_count)
    d.metric("Descriptions", google_ads.description_count)
    k.metric("Keywords", google_ads.keyword_count)

    st.markdown("### Headlines")
    for index, headline in enumerate(google_ads.headlines, start=1):
        st.write(f"{index}. {headline}")

    st.markdown("### Descriptions")
    for index, description in enumerate(google_ads.descriptions, start=1):
        st.write(f"{index}. {description}")

    keyword_column, negative_keyword_column = st.columns(2)

    with keyword_column:
        st.markdown("### Keywords")
        for keyword in google_ads.keywords:
            st.write(f"- {keyword}")

    with negative_keyword_column:
        st.markdown("### Negative Keywords")
        for negative_keyword in google_ads.negative_keywords:
            st.write(f"- {negative_keyword}")

    st.markdown("### Recommended Call to Action")
    st.write(google_ads.call_to_action)

    google_ads_text = google_ads.to_plain_text()

    st.download_button(
        label="Download Google Ads as TXT",
        data=google_ads_text,
        file_name="yaffiliate_campaign_google_ads.txt",
        mime="text/plain",
        width="stretch",
        key="download_campaign_google_ads",
    )


def _render_campaign_export(campaign: CampaignPackage) -> None:
    st.divider()
    st.subheader("Export complete campaign")

    st.caption(
        "Download the campaign as structured JSON "
        "or as a complete ZIP package."
    )

    try:
        campaign_json = campaign_export_service.to_json(campaign)
        campaign_zip = zip_exporter.campaign_to_bytes(campaign)
    except Exception as error:
        st.exception(error)
        return

    safe_campaign_name = _sanitize_download_file_name(
        campaign.campaign_name
    )

    json_column, zip_column = st.columns(2)

    with json_column:
        st.download_button(
            label="📄 Download campaign JSON",
            data=campaign_json,
            file_name=f"{safe_campaign_name}.json",
            mime="application/json",
            width="stretch",
            key="download_complete_campaign_json",
        )

    with zip_column:
        st.download_button(
            label="📦 Download complete campaign ZIP",
            data=campaign_zip,
            file_name=f"{safe_campaign_name}.zip",
            mime="application/zip",
            width="stretch",
            key="download_complete_campaign_zip",
        )


def _build_article_text(article: SEOArticle) -> str:
    blocks = [
        article.title,
        "",
        f"Meta Description\n{article.meta_description}",
        "",
        f"Introduction\n{article.introduction}",
    ]

    for section in article.sections:
        blocks.extend(["", section.heading, section.content])

    blocks.extend(
        [
            "",
            "Conclusion",
            article.conclusion,
            "",
            "Call to Action",
            article.call_to_action,
        ]
    )

    return "\n".join(blocks).strip()


def _build_landing_page_text(landing_page: LandingPage) -> str:
    blocks = [
        landing_page.page_title,
        "",
        f"Meta Description\n{landing_page.meta_description}",
        "",
        landing_page.hero_headline,
        landing_page.hero_subheadline,
        "",
        f"Primary Call to Action\n{landing_page.primary_cta}",
    ]

    for section in landing_page.sections:
        blocks.extend(["", section.heading, section.content])

        for item in section.items:
            blocks.append(f"- {item}")

    blocks.extend(
        [
            "",
            landing_page.final_cta_heading,
            landing_page.final_cta_text,
            "",
            f"Final Call to Action\n{landing_page.final_cta_button}",
        ]
    )

    return "\n".join(blocks).strip()


def _sanitize_download_file_name(value: str) -> str:
    cleaned_value = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        value.strip(),
    )

    cleaned_value = re.sub(
        r"_+",
        "_",
        cleaned_value,
    ).strip("_")

    return cleaned_value or "yaffiliate_campaign"


def _validate_campaign_fields(
    *,
    target_keyword: str,
    target_audience: str,
    campaign_name: str,
) -> list[str]:
    missing_fields: list[str] = []

    if not target_keyword.strip():
        missing_fields.append("Target keyword")

    if not target_audience.strip():
        missing_fields.append("Target audience")

    if not campaign_name.strip():
        missing_fields.append("Campaign name")

    return missing_fields