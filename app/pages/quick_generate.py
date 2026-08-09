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

# NOTE:
# This is the reconstructed version based on the code you shared.
# It includes:
# - Correct __future__ import
# - Supabase save
# - Campaign ID in session
# - Better exception display (st.exception)
#
# Keep the remainder of your helper functions
# (_render_result, _render_deliverables, _safe_file_name, etc.)
# exactly as they were in your project.

def render() -> None:
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
        placeholder="Examples: Excel Masterclass, English Course",
    )

    if not st.button("🚀 Generate My Campaign", type="primary"):
        return

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
                selected_product = _build_custom_product(cleaned_query)
                products = [selected_product]
            else:
                selected_product = products[0]

            comparison = comparison_service.compare(products)

            selected_comparison = next(
                (
                    item
                    for item in comparison.products
                    if item.product.product_name
                    == selected_product.product_name
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
                target_audience="People interested in this product",
                tone="Professional",
                article_length="Medium",
                primary_goal="Visit Sales Page",
                email_count=3,
                campaign_name=f"{selected_product.product_name} Marketing Kit",
            )

            campaign_zip = zip_exporter.campaign_to_bytes(campaign)

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
                if response.data
                else None
            )

        st.session_state["quick_generated_campaign"] = campaign
        st.session_state["quick_generated_zip"] = campaign_zip
        st.session_state["quick_generated_custom_product"] = used_custom_product
        st.session_state["quick_generated_campaign_id"] = campaign_id

        st.success("Marketing kit generated and saved.")

    except Exception as error:
        st.exception(error)
