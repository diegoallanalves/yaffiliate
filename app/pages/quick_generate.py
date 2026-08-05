"""Quick Generate page for YAffiliate.

This page offers the fastest path from a product idea to a complete
affiliate-marketing campaign ZIP.

The first version searches products by name or keyword. Direct Hotmart URL
import can be added later after the product-link parser is implemented.
"""

from __future__ import annotations

import re

import streamlit as st

from app.collectors.hotmart_collector import HotmartCollector
from app.components.layout import page_header
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
zip_exporter = ZipExporter()


def render() -> None:
    """Render the simple YAffiliate marketing-kit generator."""

    page_header(
        "AI Marketing Kit",
        "Create a complete affiliate campaign from one product.",
        (
            "Search for a product, generate the campaign, "
            "and download the complete ZIP package."
        ),
    )

    st.info(
        "For this first version, enter a product name or keyword. "
        "Direct Hotmart-link import will be added later."
    )

    product_query = st.text_input(
        "Product name or keyword",
        value="Excel",
        placeholder="Example: Excel, English, AI, Finance",
        key="quick_generate_product_query",
    )

    generate = st.button(
        "🚀 Create My Marketing Kit",
        type="primary",
        width="stretch",
        key="quick_generate_button",
    )

    if generate:
        if not product_query.strip():
            st.error("Enter a product name or keyword.")
            return

        try:
            with st.spinner(
                "Finding the product and creating your marketing kit..."
            ):
                products = collector.search_products(
                    keyword=product_query.strip(),
                    country_code="BR",
                    language_code="pt-BR",
                    limit=10,
                )

                if not products:
                    st.warning(
                        "No products were found. Try another keyword."
                    )
                    return

                selected_product = products[0]
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
                    target_keyword=product_query.strip(),
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

                campaign_zip = zip_exporter.campaign_to_bytes(campaign)

            st.session_state["quick_generated_campaign"] = campaign
            st.session_state["quick_generated_zip"] = campaign_zip
            st.success("Your marketing kit is ready.")

        except Exception as error:
            st.error(
                "The marketing kit could not be created. "
                f"{error}"
            )
            return

    campaign = st.session_state.get("quick_generated_campaign")
    campaign_zip = st.session_state.get("quick_generated_zip")

    if not isinstance(campaign, CampaignPackage):
        _render_deliverables()
        return

    _render_result(campaign=campaign, campaign_zip=campaign_zip)


def _render_deliverables() -> None:
    """Show what the customer receives."""

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
) -> None:
    """Render the generated campaign summary and download button."""

    st.divider()
    st.subheader("Marketing Kit Ready")

    st.write(f"**Product:** {campaign.product_name}")
    st.write(f"**Campaign:** {campaign.campaign_name}")

    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric("Files ready", campaign.asset_count)
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

    if not isinstance(campaign_zip, bytes):
        st.error("The ZIP file is not available. Generate the kit again.")
        return

    safe_name = _safe_file_name(campaign.campaign_name)

    st.download_button(
        label="📦 Download My Complete Marketing Kit",
        data=campaign_zip,
        file_name=f"{safe_name}.zip",
        mime="application/zip",
        type="primary",
        width="stretch",
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

    cleaned_value = re.sub(r"_+", "_", cleaned_value).strip("_")

    return cleaned_value or "yaffiliate_marketing_kit"
