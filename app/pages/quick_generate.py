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
from app.services.translation_service import t


collector = HotmartCollector()
comparison_service = ComparisonService()
analysis_service = ProductAnalysisService()
campaign_service = CampaignGeneratorService()
campaign_repository = CampaignRepository()
zip_exporter = ZipExporter()


def render() -> None:
    """Render the quick campaign generator."""

    # ---------------------------------------------------------
    # Page header
    # ---------------------------------------------------------
    page_header(
        t("qg_eyebrow"),
        t("qg_title"),
        t("qg_subtitle"),
    )

    st.info(
        t("qg_info")
    )

    # ---------------------------------------------------------
    # Product search
    # ---------------------------------------------------------
    product_query = st.text_input(
        t("qg_product_question"),
        value="",
        placeholder=t("qg_product_placeholder"),
        key="quick_generate_product_query",
    )

    generate = st.button(
        t("qg_generate"),
        type="primary",
        key="quick_generate_button",
    )

    # ---------------------------------------------------------
    # Generate campaign
    # ---------------------------------------------------------
    if generate:
        cleaned_query = product_query.strip()

        if not cleaned_query:
            st.error(
                t("qg_enter_product")
            )
            return

        try:
            with st.spinner(
                t("qg_generating")
            ):
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

                comparison = comparison_service.compare(
                    products
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

                # -------------------------------------------------
                # IMPORTANT:
                # These values are internal generation parameters.
                # They are deliberately kept stable so translating
                # the UI does not change campaign logic.
                # -------------------------------------------------
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

                user_id = st.session_state.get(
                    "auth_user_id"
                )

                if not user_id:
                    st.error(
                        t("qg_session_expired")
                    )
                    return

                response = campaign_repository.save_campaign(
                    user_id=user_id,
                    product_name=campaign.product_name,
                    campaign=campaign_data,
                )

                campaign_id = (
                    response.data[0]["id"]
                    if getattr(response, "data", None)
                    else None
                )

            # -----------------------------------------------------
            # Store generated campaign in Streamlit session
            # -----------------------------------------------------
            st.session_state[
                "quick_generated_campaign"
            ] = campaign

            st.session_state[
                "quick_generated_zip"
            ] = campaign_zip

            st.session_state[
                "quick_generated_custom_product"
            ] = used_custom_product

            st.session_state[
                "quick_generated_campaign_id"
            ] = campaign_id

            st.success(
                t("qg_generated")
            )

        except Exception as error:
            st.exception(error)
            return

    # ---------------------------------------------------------
    # Load generated campaign from session
    # ---------------------------------------------------------
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

    if not isinstance(
        campaign,
        CampaignPackage,
    ):
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

    # These are internal fallback values.
    # They should not change when the interface language changes.
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

    st.subheader(
        t("qg_kit_include")
    )

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown(
            f"✅ {t('qg_seo_article')}"
        )
        st.markdown(
            f"✅ {t('qg_landing_page')}"
        )
        st.markdown(
            f"✅ {t('qg_email_sequence')}"
        )

    with right_column:
        st.markdown(
            f"✅ {t('qg_google_ads')}"
        )
        st.markdown(
            f"✅ {t('qg_campaign_summary')}"
        )
        st.markdown(
            f"✅ {t('qg_zip_package')}"
        )


def _render_result(
    *,
    campaign: CampaignPackage,
    campaign_zip: bytes | None,
    used_custom_product: bool,
) -> None:
    """Render the generated campaign result."""

    st.divider()

    st.subheader(
        t("qg_ready")
    )

    # ---------------------------------------------------------
    # Product-data warning
    # ---------------------------------------------------------
    if used_custom_product:
        st.warning(
            t("qg_placeholder_warning")
        )

    # ---------------------------------------------------------
    # Campaign information
    # ---------------------------------------------------------
    st.write(
        f"**{t('qg_product')}:** "
        f"{campaign.product_name}"
    )

    st.write(
        f"**{t('qg_campaign')}:** "
        f"{campaign.campaign_name}"
    )

    # ---------------------------------------------------------
    # Campaign metrics
    # ---------------------------------------------------------
    metric_1, metric_2, metric_3 = st.columns(3)

    metric_1.metric(
        t("qg_files_ready"),
        campaign.asset_count,
    )

    metric_2.metric(
        t("qg_marketing_content"),
        (
            f"{campaign.total_estimated_words:,} "
            f"{t('qg_words')}"
        ),
    )

    metric_3.metric(
        t("qg_average_quality"),
        f"{campaign.average_quality_score:.1f}/100",
    )

    # ---------------------------------------------------------
    # Included assets
    # ---------------------------------------------------------
    st.markdown(
        f"### {t('qg_included')}"
    )

    included_columns = st.columns(4)

    included_columns[0].success(
        t("qg_seo_article")
    )

    included_columns[1].success(
        t("qg_landing_page")
    )

    included_columns[2].success(
        t("qg_email_sequence")
    )

    included_columns[3].success(
        t("qg_google_ads")
    )

    # ---------------------------------------------------------
    # Saved campaign
    # ---------------------------------------------------------
    campaign_id = st.session_state.get(
        "quick_generated_campaign_id"
    )

    if campaign_id:
        st.caption(
            f"{t('qg_saved_id')}: {campaign_id}"
        )

    # ---------------------------------------------------------
    # ZIP download
    # ---------------------------------------------------------
    if not isinstance(
        campaign_zip,
        bytes,
    ):
        st.error(
            t("qg_zip_unavailable")
        )
        return

    safe_name = _safe_file_name(
        campaign.campaign_name
    )

    st.download_button(
        label=t("qg_download"),
        data=campaign_zip,
        file_name=f"{safe_name}.zip",
        mime="application/zip",
        type="primary",
        key="quick_download_marketing_kit",
    )

    st.caption(
        t("qg_zip_caption")
    )


def _safe_file_name(
    value: str,
) -> str:
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

    return (
        cleaned_value
        or "yaffiliate_marketing_kit"
    )