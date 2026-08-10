"""Quick Generate page for YAffiliate."""

from __future__ import annotations

import json
import re
from dataclasses import asdict

import streamlit as st

from app.collectors.hotmart_collector import HotmartCollector
from app.components.layout import page_header
from app.models.discovery_product import DiscoveryProduct
from app.repositories.campaign_repository import CampaignRepository
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
campaign_repository = CampaignRepository()
zip_exporter = ZipExporter()


def render() -> None:
    """Render the quick campaign generator."""

    page_header(
        "START HERE",
        "From One Product to a Complete Marketing Campaign in Minutes.",
        (
            "Search for a product, generate the campaign, "
            "and download the complete ZIP package."
        ),
    )

    st.info(
        "Search any product and YAffiliate will create a complete "
        "marketing campaign in minutes."
    )

    product_query = st.text_input(
        "What product do you want to promote?",
        value="",
        placeholder="Examples: Excel Masterclass, English Course",
        key="quick_generate_product_query",
    )

    generate = st.button(
        "🚀 Generate My Campaign",
        type="primary",
        key="quick_generate_button",
    )

    if generate:
        cleaned_query = product_query.strip()

        if not cleaned_query:
            st.error("Enter a product name.")
            return

        try:
            with st.spinner("Generating campaign..."):
                products = collector.search_products(
                    keyword=cleaned_query,
                    country_code="BR",
                    language_code="pt-BR",
                    limit=10,
                )

                used_custom_product = not products

                if used_custom_product:
                    selected_product = _build_custom_product(
                        cleaned_query
                    )
                    products = [selected_product]
                else:
                    selected_product = products[0]

                comparison = comparison_service.compare(products)

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
                    target_keyword=cleaned_query,
                    target_audience=(
                        "People interested in this product who want "
                        "a clear solution to their problem"
                    ),
                    tone="Professional",
                    article_length="Medium",
                    primary_goal="Visit Sales Page",
                    email_count=3,
                    campaign_name=(
                        f"{selected_product.product_name} Marketing Kit"
                    ),
                )

                campaign_zip = zip_exporter.campaign_to_bytes(
                    campaign
                )

                campaign_data = json.dumps(
                    asdict(campaign),
                    default=str,
                    ensure_ascii=False,
                )

                response = campaign_repository.save_campaign(
                    user_id="beta-test-user",
                    product_name=campaign.product_name,
                    campaign=campaign_data,
                )

                campaign_id = (
                    response.data[0]["id"]
                    if getattr(response, "data", None)
                    else None
                )

            st.session_state["quick_generated_campaign"] = campaign
            st.session_state["quick_generated_zip"] = campaign_zip
            st.session_state[
                "quick_generated_custom_product"
            ] = used_custom_product
            st.session_state[
                "quick_generated_campaign_id"
            ] = campaign_id

            st.success("Marketing kit generated and saved.")

        except Exception as error:
            st.exception(error)
            return

    campaign = st.session_state.get(
        "quick_generated_campaign"
    )
    campaign_zip = st.session_state.get(
        "quick_generated_zip"
    )
    used_custom_product = bool(
        st.session_state.get(
            "quick_generated_custom_product"
        )
    )

    if not isinstance(campaign, CampaignPackage):
        _render_deliverables()
        return

    _render_result(
        campaign=campaign,
        campaign_zip=campaign_zip,
        used_custom_product=used_custom_product,
    )


def _build_custom_product(
    product_name: str,
) -> DiscoveryProduct:
    """Create a temporary custom product for quick generation."""

    return DiscoveryProduct(
        product_name=product_name,
        network_name="Custom Product",
        category="General",
        country_code="BR",
        language_code="pt-BR",
        price=197.00,
        commission_amount=80.00,
        commission_percent=40.00,
        epc=1.00,
        gravity_score=20.00,
        search_volume=1000,
        competition_score=50.00,
        estimated_cpc=1.50,
        google_trend_score=50.00,
        refund_rate=5.00,
        opportunity_score=50.00,
        sales_page_url=None,
        affiliate_url=None,
        description=(
            f"Custom affiliate product named {product_name}. "
            "Commercial and market values are placeholders for testing."
        ),
    )


def _render_deliverables() -> None:
    """Show what the generated marketing kit includes."""

    st.divider()
    st.subheader("Your marketing kit will include")

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown("✅ SEO article")
        st.markdown("✅ Landing page")
        st.markdown("✅ Email sequence")

    with right_column:
        st.markdown("✅ Google Ads")
        st.markdown("✅ Campaign summary")
        st.markdown("✅ Complete ZIP package")


def _render_result(
    *,
    campaign: CampaignPackage,
    campaign_zip: bytes | None,
    used_custom_product: bool,
) -> None:
    """Render the generated campaign result."""

    st.divider()
    st.subheader("Marketing Kit Ready")

    if used_custom_product:
        st.warning(
            "This campaign used estimated placeholder product data "
            "because the product was not found in the catalogue."
        )

    st.write(f"**Product:** {campaign.product_name}")
    st.write(f"**Campaign:** {campaign.campaign_name}")

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        "Files ready",
        campaign.asset_count,
    )
    metric_2.metric(
        "Marketing content",
        f"{campaign.total_estimated_words:,} words",
    )
    metric_3.metric(
        "Average quality",
        f"{campaign.average_quality_score:.1f}/100",
    )

    st.markdown("### Included")

    included_columns = st.columns(4)
    included_columns[0].success("SEO Article")
    included_columns[1].success("Landing Page")
    included_columns[2].success("Email Sequence")
    included_columns[3].success("Google Ads")

    campaign_id = st.session_state.get(
        "quick_generated_campaign_id"
    )

    if campaign_id:
        st.caption(
            f"Saved Campaign ID: {campaign_id}"
        )

    if not isinstance(campaign_zip, bytes):
        st.error(
            "The ZIP file is not available. Generate the kit again."
        )
        return

    safe_name = _safe_file_name(
        campaign.campaign_name
    )

    st.download_button(
        label="📦 Download My Complete Marketing Kit",
        data=campaign_zip,
        file_name=f"{safe_name}.zip",
        mime="application/zip",
        type="primary",
        key="quick_download_marketing_kit",
    )

    st.caption(
        "The ZIP includes the campaign assets and summary files "
        "created by YAffiliate."
    )


def _safe_file_name(value: str) -> str:
    """Convert a campaign name into a safe ZIP file name."""

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

    return cleaned_value or "yaffiliate_marketing_kit"
