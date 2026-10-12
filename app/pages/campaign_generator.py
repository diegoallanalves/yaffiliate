
"""Campaign Generator page for YAffiliate."""

from __future__ import annotations

import re
import math

import streamlit as st

from app.services.translation_service import ui
from app.collectors.hotmart_collector import HotmartCollector
from app.services.auth_service import AuthService
from app.components.layout import navigate_to, page_header
from app.models.discovery_product import DiscoveryProduct
from app.models.email_sequence import EmailSequence
from app.models.google_ads_campaign import GoogleAdsAsset
from app.models.landing_page import LandingPage
from app.models.seo_article import SEOArticle
from app.repositories.product_repository import ProductRepository
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


def _number(value, default=0.0):
    """Convert a nullable database metric into a finite number."""
    try:
        if value is None or value == "":
            return default
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _text(value, default=""):
    """Convert optional text into a safe string."""
    return str(value).strip() if value is not None else default


def _saved_product_to_discovery(row):
    """
    Adapt an authenticated Supabase product to DiscoveryProduct.

    Missing numeric fields are converted to zero only because the
    existing analysis engine requires numeric values. Zero here
    must not be interpreted as verified market evidence.
    """
    return DiscoveryProduct(
        product_name=_text(row.get("ProductName")),
        network_name=_text(
            row.get("NetworkName"), "Not specified"
        ) or "Not specified",
        category=row.get("Category"),
        country_code=row.get("CountryCode"),
        language_code=row.get("LanguageCode"),
        price=_number(row.get("Price")),
        commission_amount=_number(row.get("CommissionAmount")),
        commission_percent=_number(row.get("CommissionPercent")),
        epc=_number(row.get("EPC")),
        gravity_score=_number(row.get("GravityScore")),
        search_volume=int(_number(row.get("SearchVolume"))),
        competition_score=_number(row.get("CompetitionScore")),
        estimated_cpc=_number(row.get("EstimatedCPC")),
        google_trend_score=_number(row.get("GoogleTrendScore")),
        refund_rate=_number(row.get("RefundRate")),
        opportunity_score=_number(row.get("OpportunityScore")),
        sales_page_url=row.get("SalesPageURL"),
        affiliate_url=row.get("AffiliateURL"),
        description=row.get("Notes"),
    )


def _load_saved_products():
    """Load the signed-in user's Supabase product catalogue."""
    return ProductRepository().list_products()


def _select_product():
    """
    Select a product from Supabase or Hotmart.

    Returns:
        (selected_product, comparison_products, source, saved_record)
    """
    st.markdown("### 1. Choose your product")

    source = st.radio(
        "Product source",
        options=["My saved products", "Discover products (Hotmart)"],
        horizontal=True,
        key="campaign_product_source",
    )

    if source == "My saved products":
        try:
            saved_products = _load_saved_products()
        except Exception as error:
            st.error("Unable to load your saved products.")
            st.caption(str(error))
            return None, [], source, None

        if not saved_products:
            st.info(
                "Your product catalogue is empty. "
                "Add a product in Product Research first."
            )
            if st.button(
                "Open Product Research",
                key="campaign_open_research",
            ):
                navigate_to("product_research")
                st.rerun()
            return None, [], source, None

        options = {
            str(row["ProductID"]): row
            for row in saved_products
            if row.get("ProductID") is not None
        }

        selected_id = st.selectbox(
            "Select a saved product",
            options=list(options),
            format_func=lambda value: (
                f"{options[value].get('ProductName', 'Unnamed')} "
                f"— {options[value].get('NetworkName') or 'Network not set'}"
            ),
            key="campaign_saved_product_id",
        )

        row = options[selected_id]
        product = _saved_product_to_discovery(row)

        st.caption(
            f"Category: {product.category or 'Not specified'} · "
            f"Status: {row.get('Status') or 'Not specified'}"
        )

        if product.commission_amount <= 0:
            st.warning(
                "No positive commission amount is recorded for this "
                "product. Verify the actual affiliate commission "
                "before publishing or paying for advertising."
            )

        if not (
            product.affiliate_url
            and str(product.affiliate_url).startswith(
                ("https://", "http://")
            )
        ):
            st.warning(
                "No valid affiliate tracking URL is recorded. "
                "You can generate draft content, but must add your "
                "own verified affiliate link before publishing."
            )

        missing_metrics = [
            name
            for name, value in [
                ("Search volume", row.get("SearchVolume")),
                ("Estimated CPC", row.get("EstimatedCPC")),
                ("EPC", row.get("EPC")),
            ]
            if value is None or _number(value) == 0
        ]

        if missing_metrics:
            st.caption(
                "Market data may be incomplete: "
                + ", ".join(missing_metrics)
                + ". Analysis results are provisional."
            )

        return product, [], source, row

    st.caption(
        "Explore products using the existing Hotmart collector."
    )

    search_keyword = st.text_input(
        "Search product keyword",
        value="Excel",
        key="campaign_hotmart_keyword",
    )

    if not search_keyword.strip():
        st.info("Enter a keyword to discover products.")
        return None, [], source, None

    try:
        products = collector.search_products(
            keyword=search_keyword.strip(),
            country_code="BR",
            language_code="pt-BR",
            limit=10,
        )
    except Exception as error:
        st.error("Product discovery is currently unavailable.")
        st.caption(str(error))
        return None, [], source, None

    if not products:
        st.info("No products found for this keyword.")
        return None, [], source, None

    selected_index = st.selectbox(
        "Select a discovered product",
        options=list(range(len(products))),
        format_func=lambda index: products[index].product_name,
        key="campaign_hotmart_product_index",
    )

    return products[selected_index], products, source, None


def _load_campaign_from_history():
    """Preserve existing Campaign History functionality."""
    loaded_campaign = st.session_state.get("loaded_campaign")

    if isinstance(loaded_campaign, dict):
        if not isinstance(
            st.session_state.get("generated_campaign"),
            CampaignPackage,
        ):
            try:
                st.session_state["generated_campaign"] = (
                    campaign_from_dict(loaded_campaign)
                )
            except Exception as error:
                st.warning(
                    ui(
                        "The saved campaign settings were loaded, "
                        "but its assets could not be reconstructed."
                    )
                )
                st.caption(str(error))

        st.success(ui("Saved campaign loaded from Campaign History."))

        if st.button(
            ui("← Back to Campaign History"),
            key="back_to_campaign_history",
        ):
            navigate_to("campaign_history")
            st.rerun()

        if st.button(
            ui("Clear loaded campaign"),
            key="clear_loaded_campaign",
        ):
            for key in [
                "loaded_campaign",
                "loaded_campaign_id",
                "generated_campaign",
                "generated_campaign_id",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

    return loaded_campaign if isinstance(loaded_campaign, dict) else {}


def render() -> None:
    """Render the YAffiliate Campaign Generator."""

    page_header(
        "Campaign Generator",
        "Create coordinated marketing assets from one product.",
        "Generate an SEO article, landing page, email sequence "
        "and Google Ads campaign.",
    )

    loaded_campaign = _load_campaign_from_history()

    selected_product, comparison_products, source, saved_row = (
        _select_product()
    )

    if selected_product is not None:
        st.divider()
        st.markdown("### 2. Configure your campaign")

        # Widget keys include the product identity so changing
        # products refreshes the suggested input values.
        product_identity = (
            f"saved_{saved_row.get('ProductID')}"
            if saved_row is not None
            else f"hotmart_{selected_product.product_name}"
        )

        loaded_product_name = _text(
            loaded_campaign.get("product_name")
        )

        using_loaded_settings = bool(loaded_campaign)

        default_keyword = (
            _text(loaded_campaign.get("target_keyword"))
            if using_loaded_settings
            else selected_product.product_name
        )

        default_audience = (
            _text(loaded_campaign.get("target_audience"))
            if using_loaded_settings
            else ""
        )

        default_name = (
            _text(loaded_campaign.get("campaign_name"))
            if using_loaded_settings
            else f"{selected_product.product_name} Affiliate Campaign"
        )

        tone_options = [
            "Professional",
            "Friendly",
            "Persuasive",
            "Educational",
        ]

        loaded_tone = _text(
            loaded_campaign.get("tone"), "Professional"
        ) or "Professional"

        tone_index = (
            tone_options.index(loaded_tone)
            if loaded_tone in tone_options
            else 0
        )

        if (
            using_loaded_settings
            and loaded_product_name
            and loaded_product_name != selected_product.product_name
        ):
            st.warning(
                "The campaign loaded from history belongs to "
                f"'{loaded_product_name}', while the selected product "
                f"is '{selected_product.product_name}'. "
                "Choose the matching product before generating "
                "a replacement campaign."
            )

        with st.form(
            f"campaign_configuration_{product_identity}"
        ):
            c1, c2 = st.columns(2)

            with c1:
                target_keyword = st.text_input(
                    ui("Target keyword"),
                    value=default_keyword,
                    key=f"campaign_keyword_{product_identity}",
                )

                target_audience = st.text_area(
                    ui("Target audience"),
                    value=default_audience,
                    placeholder=(
                        "Describe who should buy this product "
                        "and why it is relevant to them."
                    ),
                    height=110,
                    key=f"campaign_audience_{product_identity}",
                )

                campaign_name = st.text_input(
                    ui("Campaign name"),
                    value=default_name,
                    key=f"campaign_name_{product_identity}",
                )

            with c2:
                tone = st.selectbox(
                    ui("Writing tone"),
                    tone_options,
                    index=tone_index,
                    key=f"campaign_tone_{product_identity}",
                )

                article_length = st.selectbox(
                    ui("SEO article length"),
                    ["Short", "Medium", "Long"],
                    index=1,
                    key=f"campaign_length_{product_identity}",
                )

                primary_goal = st.selectbox(
                    ui("Campaign goal"),
                    [
                        "Visit Sales Page",
                        "Generate Leads",
                        "Promote Product",
                    ],
                    key=f"campaign_goal_{product_identity}",
                )

                email_count = st.selectbox(
                    ui("Email sequence length"),
                    [3, 4, 5],
                    format_func=lambda count: f"{count} emails",
                    key=f"campaign_emails_{product_identity}",
                )

            generate_campaign = st.form_submit_button(
                ui("🚀 Generate Campaign"),
                type="primary",
                use_container_width=True,
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
            else:
                try:
                    user_id = AuthService().get_current_user_id()

                    if not user_id:
                        st.error(
                            ui(
                                "You must be signed in "
                                "to save a campaign."
                            )
                        )
                    else:
                        with st.spinner(
                            "Analysing product and generating campaign..."
                        ):
                            selected_comparison = None

                            if comparison_products:
                                comparison = comparison_service.compare(
                                    comparison_products
                                )

                                selected_comparison = next(
                                    (
                                        item
                                        for item in comparison.products
                                        if (
                                            item.product.product_name
                                            == selected_product.product_name
                                        )
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

                            campaign_json = (
                                campaign_export_service.to_json(campaign)
                            )

                            saved_response = (
                                campaign_repository.save_campaign(
                                    user_id=user_id,
                                    product_name=campaign.product_name,
                                    campaign=campaign_json,
                                )
                            )

                            saved_id = (
                                saved_response.data[0]["id"]
                                if getattr(saved_response, "data", None)
                                else None
                            )

                        st.session_state["generated_campaign"] = campaign
                        st.session_state["generated_campaign_id"] = saved_id
                        st.session_state.pop("loaded_campaign", None)
                        st.session_state.pop("loaded_campaign_id", None)

                        st.success(
                            ui(
                                "Campaign generated and saved "
                                "to Campaign History."
                            )
                        )
                        st.rerun()

                except Exception as error:
                    st.error("Campaign generation failed.")
                    st.exception(error)

    st.divider()
    st.markdown("### 3. Generated campaign assets")

    campaign = st.session_state.get("generated_campaign")

    if not isinstance(campaign, CampaignPackage):
        st.info(
            "Select a product, configure your campaign "
            "and generate the marketing assets."
        )
        return

    _render_campaign_summary(campaign)
    _render_campaign_assets(campaign)
    _render_campaign_export(campaign)


def _render_campaign_summary(campaign: CampaignPackage) -> None:
    st.divider()
    st.subheader(campaign.campaign_name)
    st.caption(f"Product: {campaign.product_name}")

    saved_id = st.session_state.get("generated_campaign_id")

    if saved_id:
        st.caption(f"Saved Campaign ID: {saved_id}")

    m1, m2, m3 = st.columns(3)

    m1.metric(ui("Campaign assets"), campaign.asset_count)
    m2.metric(
        ui("Estimated words"),
        f"{campaign.total_estimated_words:,}",
    )
    m3.metric(
        ui("Average quality"),
        f"{campaign.average_quality_score:.1f}/100",
    )

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
        st.write(
            campaign.created_at.strftime(
                "%d %B %Y, %H:%M UTC"
            )
        )


def _render_campaign_assets(campaign: CampaignPackage) -> None:
    st.divider()

    article_tab, landing_tab, email_tab, ads_tab = st.tabs(
        [
            ui("📰 SEO Article"),
            ui("🌐 Landing Page"),
            ui("📧 Email Sequence"),
            ui("🎯 Google Ads"),
        ]
    )

    with article_tab:
        _render_seo_article(campaign.seo_article)

    with landing_tab:
        _render_landing_page(campaign.landing_page)

    with email_tab:
        _render_email_sequence(campaign.email_sequence)

    with ads_tab:
        _render_google_ads(campaign.google_ads)


def _render_seo_article(article: SEOArticle) -> None:
    st.subheader(article.title)

    m1, m2 = st.columns(2)
    m1.metric(ui("SEO score"), f"{article.seo_score:.1f}/100")
    m2.metric(
        ui("Estimated words"),
        f"{article.estimated_word_count:,}",
    )

    article_text = _build_article_text(article)

    st.text_area(
        ui("SEO article content"),
        value=article_text,
        height=520,
        key="campaign_seo_article_preview",
    )

    st.download_button(
        label="Download SEO article as TXT",
        data=article_text,
        file_name="yaffiliate_campaign_seo_article.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_campaign_article",
    )


def _render_landing_page(landing_page: LandingPage) -> None:
    st.subheader(landing_page.page_title)

    m1, m2 = st.columns(2)
    m1.metric(
        ui("Conversion score"),
        f"{landing_page.conversion_score:.1f}/100",
    )
    m2.metric(
        ui("Estimated words"),
        f"{landing_page.estimated_word_count:,}",
    )

    content = _build_landing_page_text(landing_page)

    st.text_area(
        ui("Landing-page content"),
        value=content,
        height=520,
        key="campaign_landing_page_preview",
    )

    st.download_button(
        label="Download landing page as TXT",
        data=content,
        file_name="yaffiliate_campaign_landing_page.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_campaign_landing_page",
    )


def _render_email_sequence(email_sequence: EmailSequence) -> None:
    st.subheader(email_sequence.sequence_name)

    m1, m2 = st.columns(2)
    m1.metric(ui("Emails"), email_sequence.email_count)
    m2.metric(
        ui("Estimated words"),
        f"{email_sequence.total_estimated_words:,}",
    )

    if email_sequence.strategy_summary:
        st.markdown("### Strategy Summary")
        st.write(email_sequence.strategy_summary)

    st.markdown("### Campaign Emails")

    for email in email_sequence.emails:
        with st.expander(
            f"Email {email.sequence_number}: {email.purpose}",
            expanded=email.sequence_number == 1,
        ):
            st.markdown("**Subject**")
            st.write(email.subject)
            st.markdown("**Preview text**")
            st.write(email.preview_text)
            st.markdown("**Email body**")
            st.write(email.body)
            st.markdown("**Call to Action**")
            st.write(email.call_to_action)

    st.download_button(
        label="Download email sequence as TXT",
        data=email_sequence.to_plain_text(),
        file_name="yaffiliate_campaign_email_sequence.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_campaign_email_sequence",
    )


def _render_google_ads(google_ads: GoogleAdsAsset) -> None:
    st.subheader(google_ads.campaign_name)

    h, d, k = st.columns(3)

    h.metric(ui("Headlines"), google_ads.headline_count)
    d.metric(ui("Descriptions"), google_ads.description_count)
    k.metric(ui("Keywords"), google_ads.keyword_count)

    st.markdown("### Headlines")
    for index, headline in enumerate(
        google_ads.headlines, start=1
    ):
        st.write(f"{index}. {headline}")

    st.markdown("### Descriptions")
    for index, description in enumerate(
        google_ads.descriptions, start=1
    ):
        st.write(f"{index}. {description}")

    keyword_column, negative_column = st.columns(2)

    with keyword_column:
        st.markdown("### Keywords")
        for keyword in google_ads.keywords:
            st.write(f"- {keyword}")

    with negative_column:
        st.markdown("### Negative Keywords")
        for keyword in google_ads.negative_keywords:
            st.write(f"- {keyword}")

    st.markdown("### Recommended Call to Action")
    st.write(google_ads.call_to_action)

    st.download_button(
        label="Download Google Ads as TXT",
        data=google_ads.to_plain_text(),
        file_name="yaffiliate_campaign_google_ads.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_campaign_google_ads",
    )


def _render_campaign_export(campaign: CampaignPackage) -> None:
    st.divider()
    st.subheader(ui("Export complete campaign"))

    st.caption(
        ui(
            "Download the campaign as structured JSON "
            "or as a complete ZIP package."
        )
    )

    try:
        campaign_json = campaign_export_service.to_json(campaign)
        campaign_zip = zip_exporter.campaign_to_bytes(campaign)
    except Exception as error:
        st.exception(error)
        return

    safe_name = _sanitize_download_file_name(
        campaign.campaign_name
    )

    json_column, zip_column = st.columns(2)

    with json_column:
        st.download_button(
            label="📄 Download campaign JSON",
            data=campaign_json,
            file_name=f"{safe_name}.json",
            mime="application/json",
            use_container_width=True,
            key="download_complete_campaign_json",
        )

    with zip_column:
        st.download_button(
            label="📦 Download complete campaign ZIP",
            data=campaign_zip,
            file_name=f"{safe_name}.zip",
            mime="application/zip",
            use_container_width=True,
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
        blocks.extend(
            ["", section.heading, section.content]
        )

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
        blocks.extend(
            ["", section.heading, section.content]
        )

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
    cleaned = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        value.strip(),
    )
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "yaffiliate_campaign"


def _validate_campaign_fields(
    *,
    target_keyword: str,
    target_audience: str,
    campaign_name: str,
) -> list[str]:
    missing = []

    if not target_keyword.strip():
        missing.append("Target keyword")

    if not target_audience.strip():
        missing.append("Target audience")

    if not campaign_name.strip():
        missing.append("Campaign name")

    return missing
