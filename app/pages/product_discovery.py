from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.layout import page_header
from app.services.comparison_service import ComparisonService
from app.services.discovery_portfolio_service import (
    DiscoveryPortfolioService,
)
from app.services.product_analysis_service import (
    ProductAnalysisService,
)
from app.services.product_discovery_service import (
    ProductDiscoveryService,
)

from app.services.business_consultant_service import (
    BusinessConsultantService,
)
from app.services.pdf_report_service import PdfReportService
from app.services.report_builder_service import (
    ReportBuilderService,
)

consultant_service = BusinessConsultantService()
report_builder = ReportBuilderService()
pdf_service = PdfReportService()

discovery_service = ProductDiscoveryService()
portfolio_service = DiscoveryPortfolioService()
comparison_service = ComparisonService()
analysis_service = ProductAnalysisService()


def render() -> None:
    page_header(
        "Product Discovery",
        "Find new affiliate opportunities.",
        (
            "Search available affiliate networks, compare products "
            "and identify the strongest opportunities."
        ),
    )

    available_networks = (
        discovery_service.list_available_networks()
    )

    with st.form("product_discovery_form"):
        keyword = st.text_input(
            "Search keyword",
            placeholder="Excel, fitness, marketing...",
        )

        selected_networks = st.multiselect(
            "Affiliate networks",
            options=available_networks,
            default=available_networks,
        )

        country_col, language_col, limit_col = st.columns(3)

        country_code = country_col.selectbox(
            "Country",
            options=[
                "BR",
                "US",
                "GB",
                "PT",
                "ES",
                "DE",
                "FR",
            ],
            index=0,
        )

        language_code = language_col.selectbox(
            "Language",
            options=[
                "pt-BR",
                "en-US",
                "en-GB",
                "pt-PT",
                "es-ES",
                "de-DE",
                "fr-FR",
            ],
            index=0,
        )

        limit_per_network = limit_col.number_input(
            "Results per network",
            min_value=1,
            max_value=100,
            value=20,
            step=1,
        )

        discover_products = st.form_submit_button(
            "Discover products",
            width="stretch",
        )

    if discover_products:
        if not keyword.strip():
            st.error(
                "Enter a keyword before searching."
            )
            return

        if not selected_networks:
            st.error(
                "Select at least one affiliate network."
            )
            return

        try:
            products = discovery_service.search(
                keyword=keyword,
                selected_networks=selected_networks,
                country_code=country_code,
                language_code=language_code,
                limit_per_network=int(
                    limit_per_network
                ),
            )

            comparison = comparison_service.compare(
                products
            )

        except Exception as exc:
            st.error(
                f"Unable to discover products: {exc}"
            )
            return

        st.session_state[
            "discovery_results"
        ] = products

        st.session_state[
            "discovery_comparison"
        ] = comparison

        st.session_state[
            "discovery_keyword"
        ] = keyword.strip()

    products = st.session_state.get(
        "discovery_results",
        [],
    )

    comparison = st.session_state.get(
        "discovery_comparison"
    )

    discovery_keyword = st.session_state.get(
        "discovery_keyword",
        "",
    )

    if not products:
        st.info(
            "Search for a keyword to discover "
            "affiliate products."
        )
        return

    st.subheader(
        f'Discovery results for "{discovery_keyword}"'
    )

    results_df = pd.DataFrame(
        [
            product.to_dict()
            for product in products
        ]
    )

    result_col1, result_col2, result_col3 = (
        st.columns(3)
    )

    result_col1.metric(
        "Products found",
        len(results_df),
    )

    result_col2.metric(
        "Best score",
        (
            f'{results_df["OpportunityScore"].max():.1f}'
            "/100"
        ),
    )

    result_col3.metric(
        "Average commission",
        (
            f'R$ '
            f'{results_df["CommissionAmount"].mean():,.2f}'
        ),
    )

    if (
        comparison is not None
        and comparison.best_product is not None
    ):
        best = comparison.best_product

        st.subheader("Best opportunity")

        best_col1, best_col2, best_col3 = (
            st.columns(3)
        )

        best_col1.metric(
            "Product",
            best.product.product_name,
        )

        best_col2.metric(
            "Opportunity score",
            (
                f"{best.product.opportunity_score:.1f}"
                "/100"
            ),
        )

        best_col3.metric(
            "Confidence",
            f"{best.confidence_score:.1f}%",
        )

        st.success(
            comparison.recommendation
        )

    display_columns = [
        "ProductName",
        "NetworkName",
        "Category",
        "Price",
        "CommissionAmount",
        "CommissionPercent",
        "SearchVolume",
        "CompetitionScore",
        "GoogleTrendScore",
        "OpportunityScore",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in results_df.columns
    ]

    table_df = results_df[
        available_columns
    ].copy()

    table_df = table_df.rename(
        columns={
            "ProductName": "Product",
            "NetworkName": "Network",
            "CommissionAmount": "Commission",
            "CommissionPercent": "Commission %",
            "SearchVolume": "Search volume",
            "CompetitionScore": "Competition",
            "GoogleTrendScore": "Trend",
            "OpportunityScore": "Score",
        }
    )

    st.dataframe(
        table_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Price": st.column_config.NumberColumn(
                "Price",
                format="R$ %.2f",
            ),
            "Commission": (
                st.column_config.NumberColumn(
                    "Commission",
                    format="R$ %.2f",
                )
            ),
            "Commission %": (
                st.column_config.NumberColumn(
                    "Commission %",
                    format="%.1f%%",
                )
            ),
            "Search volume": (
                st.column_config.NumberColumn(
                    "Search volume",
                    format="%d",
                )
            ),
            "Competition": (
                st.column_config.ProgressColumn(
                    "Competition",
                    min_value=0,
                    max_value=100,
                    format="%.0f",
                )
            ),
            "Trend": (
                st.column_config.ProgressColumn(
                    "Trend",
                    min_value=0,
                    max_value=100,
                    format="%.0f",
                )
            ),
            "Score": (
                st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                )
            ),
        },
    )

    if comparison is not None:
        st.divider()
        st.subheader("Product comparison")

        comparison_columns = st.columns(
            len(comparison.products)
        )

        for column, item in zip(
            comparison_columns,
            comparison.products,
        ):
            product = item.product

            with column:
                st.markdown(
                    f"### {item.badge}"
                )

                st.markdown(
                    f"**{product.product_name}**"
                )

                st.metric(
                    "Rank",
                    item.rank,
                )

                st.metric(
                    "Score",
                    (
                        f"{product.opportunity_score:.1f}"
                        "/100"
                    ),
                )

                st.metric(
                    "Commission",
                    (
                        f"R$ "
                        f"{product.commission_amount:,.2f}"
                    ),
                )

                st.metric(
                    "SEO rating",
                    (
                        "★" * item.seo_rating
                        + "☆"
                        * (
                            5
                            - item.seo_rating
                        )
                    ),
                )

                st.write(
                    f"**Decision:** {item.decision}"
                )

                st.write(
                    f"**Competition:** "
                    f"{product.competition_score:.0f}/100"
                )

                st.write(
                    f"**Trend:** "
                    f"{product.google_trend_score:.0f}/100"
                )

                st.write(
                    f"**EPC:** {product.epc:.2f}"
                )

                with st.expander("Strengths"):
                    for strength in item.strengths:
                        st.write(
                            f"✓ {strength}"
                        )

                with st.expander("Weaknesses"):
                    for weakness in item.weaknesses:
                        st.write(
                            f"• {weakness}"
                        )

        st.subheader("Category winners")

        for winner in comparison.winners:
            st.markdown(
                f"""
                **{winner.category}**

                {winner.product_name} — {winner.value}

                {winner.reason}
                """
            )

        st.info(
            (
                "Overall comparison confidence: "
                f"{comparison.confidence_score:.1f}%"
            )
        )

    st.divider()
    st.subheader("Inspect a discovered product")

    product_options = {
        index: product.product_name
        for index, product in enumerate(
            products
        )
    }

    selected_product_index = st.selectbox(
        "Select a product",
        options=list(
            product_options.keys()
        ),
        format_func=lambda index: (
            product_options[index]
        ),
    )

    selected_product = products[
        selected_product_index
    ]

    selected_comparison = None

    if comparison is not None:
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

    product_analysis = analysis_service.analyse(
        product=selected_product,
        comparison=selected_comparison,
    )

    consultant_report = consultant_service.generate(
        product=selected_product,
        analysis=product_analysis,
    )

    report_data = report_builder.build(
        product=selected_product,
        analysis=product_analysis,
        consultant=consultant_report,
        generated_for="Diego Alves",
    )

    pdf_bytes = pdf_service.generate(
        report_data
    )

    detail_col1, detail_col2, detail_col3 = (
        st.columns(3)
    )

    detail_col1.metric(
        "Opportunity score",
        (
            f"{selected_product.opportunity_score:.1f}"
            "/100"
        ),
    )

    detail_col2.metric(
        "Commission",
        (
            f"R$ "
            f"{selected_product.commission_amount:,.2f}"
        ),
    )

    detail_col3.metric(
        "Monthly searches",
        f"{selected_product.search_volume:,}",
    )

    st.write(
        f"**Network:** "
        f"{selected_product.network_name}"
    )

    st.write(
        f"**Category:** "
        f"{selected_product.category or 'Not available'}"
    )

    st.write(
        f"**Description:** "
        f"{selected_product.description or 'Not available'}"
    )

    st.write(
        f"**Competition:** "
        f"{selected_product.competition_score:.0f}/100"
    )

    st.write(
        f"**Google Trend:** "
        f"{selected_product.google_trend_score:.0f}/100"
    )

    st.write(
        f"**EPC:** "
        f"{selected_product.epc:.2f}"
    )

    st.write(
        f"**Refund rate:** "
        f"{selected_product.refund_rate:.1f}%"
    )

    if selected_product.sales_page_url:
        st.link_button(
            "Open sales page",
            selected_product.sales_page_url,
        )

    st.divider()
    st.subheader("AI Product Analyst")

    st.markdown(
        f"### {product_analysis.headline}"
    )

    analysis_col1, analysis_col2, analysis_col3 = (
        st.columns(3)
    )

    analysis_col1.metric(
        "Probability of success",
        (
            f"{product_analysis.probability_of_success:.1f}%"
        ),
    )

    analysis_col2.metric(
        "Confidence",
        (
            f"{product_analysis.confidence_score:.1f}%"
        ),
    )

    analysis_col3.metric(
        "Commercial potential",
        product_analysis.commercial_potential,
    )

    st.subheader("Channel potential")

    potential_col1, potential_col2 = (
        st.columns(2)
    )

    with potential_col1:
        st.metric(
            "SEO potential",
            product_analysis.seo_potential,
        )

        st.metric(
            "Google Ads potential",
            product_analysis.google_ads_potential,
        )

    with potential_col2:
        st.metric(
            "Email marketing potential",
            product_analysis.email_marketing_potential,
        )

        st.metric(
            "Landing-page potential",
            product_analysis.landing_page_potential,
        )

    audience_col, strengths_col = st.columns(2)

    with audience_col:
        st.markdown("#### Target audience")

        for audience in product_analysis.target_audience:
            st.write(
                f"• {audience}"
            )

    with strengths_col:
        st.markdown("#### Strengths")

        for strength in product_analysis.strengths:
            st.write(
                f"✓ {strength}"
            )

    st.markdown("#### Weaknesses")

    for weakness in product_analysis.weaknesses:
        st.write(
            f"• {weakness}"
        )

    st.markdown("#### Recommended strategy")

    for index, recommendation in enumerate(
        product_analysis.recommendations,
        start=1,
    ):
        st.write(
            f"{index}. {recommendation}"
        )

    st.divider()

    safe_product_name = (
        selected_product.product_name
        .strip()
        .lower()
        .replace(" ", "_")
    )

    st.download_button(
        label="📄 Download Executive Report",
        data=pdf_bytes,
        file_name=(
            f"filtrify_{safe_product_name}_report.pdf"
        ),
        mime="application/pdf",
        width="stretch",
    )

    save_product = st.button(
        "⭐ Save selected product to portfolio",
        type="primary",
        width="stretch",
    )

    if save_product:
        try:
            result = (
                portfolio_service.save_to_portfolio(
                    selected_product
                )
            )

            if result["already_exists"]:
                st.warning(
                    (
                        f'{result["product_name"]} already '
                        "exists in your portfolio. "
                        f'Product ID: '
                        f'{result["product_id"]}.'
                    )
                )

                st.info(
                    (
                        "No duplicate product, metric, "
                        "recommendation or history snapshot "
                        "was created."
                    )
                )

            else:
                st.success(
                    (
                        f'{result["product_name"]} was '
                        "saved successfully. "
                        f'Product ID: '
                        f'{result["product_id"]}. '
                        f'Recommendation ID: '
                        f'{result["recommendation_id"]}. '
                        f'History ID: '
                        f'{result["history_id"]}.'
                    )
                )

        except Exception as exc:
            st.exception(exc)