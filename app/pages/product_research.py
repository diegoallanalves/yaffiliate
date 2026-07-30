from __future__ import annotations

from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.layout import page_header
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import (
    RecommendationRepository,
)
from app.services.opportunity_score_service import (
    OpportunityFactors,
    OpportunityScoreService,
)
from app.services.recommendation_service import RecommendationService

from app.repositories.opportunity_history_repository import (
    OpportunityHistoryRepository,
)

opportunity_history_repo = OpportunityHistoryRepository()

repo = ProductRepository()
recommendation_repo = RecommendationRepository()

score_service = OpportunityScoreService()
recommendation_service = RecommendationService()


def decimal_to_float(value: object) -> float | None:
    """Convert SQL Server Decimal values into Python floats."""
    if value is None:
        return None

    if isinstance(value, Decimal):
        return float(value)

    return float(value)


def render() -> None:
    page_header(
        "Research workspace",
        "Find and compare affiliate opportunities.",
        (
            "Store product economics, demand, competition and historical "
            "metrics directly in SQL Server."
        ),
    )

    try:
        networks = repo.list_affiliate_networks()

    except Exception as exc:
        st.error(f"Unable to load affiliate networks: {exc}")
        networks = []

    network_options = {
        int(network["NetworkID"]): str(network["NetworkName"])
        for network in networks
    }

    with st.expander(
        "Add a product",
        expanded=True,
    ):
        with st.form(
            "add_product_form",
            clear_on_submit=True,
        ):
            row1_col1, row1_col2, row1_col3 = st.columns(3)

            product_name = row1_col1.text_input(
                "Product name"
            )

            selected_network_id = row1_col2.selectbox(
                "Affiliate network",
                options=[None] + list(network_options.keys()),
                format_func=lambda network_id: (
                    "Not selected"
                    if network_id is None
                    else network_options[network_id]
                ),
            )

            category = row1_col3.text_input(
                "Category"
            )

            row2_col1, row2_col2, row2_col3 = st.columns(3)

            country_code = row2_col1.text_input(
                "Country code",
                value="BR",
                max_chars=10,
            )

            language_code = row2_col2.text_input(
                "Language code",
                value="pt-BR",
                max_chars=20,
            )

            status_options = [
                "Research",
                "Shortlist",
                "Testing",
                "Active",
                "Paused",
                "Rejected",
                "Archived",
            ]

            status = row2_col3.selectbox(
                "Status",
                status_options,
            )

            row3_col1, row3_col2, row3_col3 = st.columns(3)

            price = row3_col1.number_input(
                "Price",
                min_value=0.0,
                step=10.0,
            )

            commission_amount = row3_col2.number_input(
                "Commission per sale",
                min_value=0.0,
                step=10.0,
            )

            commission_percent = row3_col3.number_input(
                "Commission %",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )

            st.subheader("Market metrics")

            row4_col1, row4_col2, row4_col3 = st.columns(3)

            epc = row4_col1.number_input(
                "EPC",
                min_value=0.0,
                step=0.1,
            )

            gravity_score = row4_col2.number_input(
                "Gravity score",
                min_value=0.0,
                step=1.0,
            )

            search_volume = row4_col3.number_input(
                "Monthly search volume",
                min_value=0,
                step=100,
            )

            row5_col1, row5_col2, row5_col3 = st.columns(3)

            competition_score = row5_col1.number_input(
                "Competition score",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )

            estimated_cpc = row5_col2.number_input(
                "Estimated CPC",
                min_value=0.0,
                step=0.1,
            )

            google_trend_score = row5_col3.number_input(
                "Google Trend score",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )

            refund_rate = st.number_input(
                "Refund rate %",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
            )

            sales_page_url = st.text_input(
                "Sales-page URL"
            )

            affiliate_url = st.text_input(
                "Affiliate URL"
            )

            notes = st.text_area(
                "Notes"
            )

            save_product = st.form_submit_button(
                "Save product to SQL Server",
                width="stretch",
            )

    if save_product:
        if not product_name.strip():
            st.error("Product name is required.")

        else:
            try:
                opportunity_factors = OpportunityFactors(
                    commission_amount=float(commission_amount),
                    commission_percent=float(commission_percent),
                    search_volume=int(search_volume),
                    competition_score=float(competition_score),
                    estimated_cpc=float(estimated_cpc),
                    google_trend_score=float(google_trend_score),
                    refund_rate=float(refund_rate),
                    gravity_score=float(gravity_score),
                    epc=float(epc),
                )

                opportunity_score = score_service.calculate(
                    opportunity_factors
                )

                product_id = repo.create_product(
                    product_name=product_name,
                    network_id=selected_network_id,
                    category=category or None,
                    language_code=language_code or None,
                    country_code=country_code or None,
                    price=float(price),
                    commission_amount=float(commission_amount),
                    commission_percent=float(commission_percent),
                    sales_page_url=sales_page_url or None,
                    affiliate_url=affiliate_url or None,
                    status=status,
                    notes=notes or None,
                )

                repo.add_product_metric(
                    product_id=product_id,
                    epc=float(epc),
                    gravity_score=float(gravity_score),
                    search_volume=int(search_volume),
                    competition_score=float(competition_score),
                    estimated_cpc=float(estimated_cpc),
                    google_trend_score=float(google_trend_score),
                    refund_rate=float(refund_rate),
                    opportunity_score=opportunity_score,
                    data_source="Manual Streamlit entry",
                )

                opportunity_history_repo.create_snapshot(
                    product_id=product_id,
                    opportunity_score=opportunity_score,
                    epc=float(epc),
                    gravity_score=float(gravity_score),
                    search_volume=int(search_volume),
                    competition_score=float(competition_score),
                    estimated_cpc=float(estimated_cpc),
                    google_trend_score=float(google_trend_score),
                    refund_rate=float(refund_rate),
                )

                recommendation = recommendation_service.generate(
                    opportunity_score=opportunity_score,
                    factors=opportunity_factors,
                )

                recommendation_id = (
                    recommendation_repo.create_recommendation(
                        product_id=product_id,
                        recommendation=recommendation,
                    )
                )

                st.session_state[
                    "latest_recommendation"
                ] = recommendation

                st.session_state[
                    "latest_recommendation_id"
                ] = recommendation_id

                st.session_state[
                    "latest_product_id"
                ] = product_id

                st.success(
                    f"Product saved successfully. "
                    f"Product ID: {product_id}. "
                    f"Recommendation ID: {recommendation_id}. "
                    f"Opportunity Score: {opportunity_score}/100"
                )

                st.rerun()

            except Exception as exc:
                st.exception(exc)

    st.subheader("Saved products")

    latest_recommendation = st.session_state.get(
        "latest_recommendation"
    )

    latest_recommendation_id = st.session_state.get(
        "latest_recommendation_id"
    )

    latest_product_id = st.session_state.get(
        "latest_product_id"
    )

    if latest_recommendation is not None:
        st.subheader("Latest Filtrify Recommendation")

        if latest_product_id is not None:
            st.caption(
                f"Product ID: {latest_product_id}"
            )

        if latest_recommendation_id is not None:
            st.caption(
                f"Recommendation ID: {latest_recommendation_id}"
            )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Opportunity",
            f"{latest_recommendation.opportunity_score:.1f}/100",
            latest_recommendation.opportunity_level,
        )

        col2.metric(
            "Risk",
            latest_recommendation.risk_level,
        )

        col3.metric(
            "Expected ROI",
            latest_recommendation.expected_roi,
        )

        st.write(
            f"**Recommended channel:** "
            f"{latest_recommendation.recommended_channel}"
        )

        st.write(
            f"**Difficulty:** "
            f"{latest_recommendation.difficulty}"
        )

        st.write(
            f"**Suggested test budget:** "
            f"R$ {latest_recommendation.recommended_budget:,.2f}"
        )

        st.markdown(
            "### Why Filtrify recommends this"
        )

        for reason in latest_recommendation.reasoning:
            st.write(f"- {reason}")

        st.markdown(
            "### Next actions"
        )

        for action in latest_recommendation.next_actions:
            st.write(f"- {action}")

    search_col, status_col = st.columns(2)

    search_text = search_col.text_input(
        "Search by product name",
        placeholder="Excel course",
    )

    status_filter = status_col.selectbox(
        "Filter by status",
        [
            "All",
            "Research",
            "Shortlist",
            "Testing",
            "Active",
            "Paused",
            "Rejected",
            "Archived",
        ],
    )

    try:
        products = repo.list_products(
            status=(
                None
                if status_filter == "All"
                else status_filter
            ),
            search=search_text or None,
        )

    except Exception as exc:
        st.error(
            f"Unable to load products: {exc}"
        )
        products = []

    if not products:
        st.info(
            "No products found in SQL Server."
        )
        return

    products_df = pd.DataFrame(
        products
    )

    numeric_columns = [
        "Price",
        "CommissionAmount",
        "CommissionPercent",
        "EPC",
        "GravityScore",
        "CompetitionScore",
        "EstimatedCPC",
        "GoogleTrendScore",
        "RefundRate",
        "OpportunityScore",
    ]

    for column in numeric_columns:
        if column in products_df.columns:
            products_df[column] = (
                products_df[column].apply(
                    lambda value: (
                        decimal_to_float(value)
                        if value is not None
                        else None
                    )
                )
            )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric(
        "Products",
        len(products_df),
    )

    average_commission = (
        products_df["CommissionAmount"]
        .fillna(0)
        .mean()
    )

    metric_col2.metric(
        "Average commission",
        f"R$ {average_commission:,.2f}",
    )

    best_score = (
        products_df["OpportunityScore"]
        .fillna(0)
        .max()
    )

    metric_col3.metric(
        "Best opportunity score",
        f"{best_score:.1f}/100",
    )

    chart_df = products_df.dropna(
        subset=[
            "EstimatedCPC",
            "CommissionAmount",
            "OpportunityScore",
        ]
    ).copy()

    if not chart_df.empty:
        chart_df["SearchVolume"] = (
            chart_df["SearchVolume"]
            .fillna(1)
            .clip(lower=1)
        )

        chart = px.scatter(
            chart_df,
            x="EstimatedCPC",
            y="CommissionAmount",
            size="SearchVolume",
            color="OpportunityScore",
            hover_name="ProductName",
            title="Commission versus estimated CPC",
            labels={
                "EstimatedCPC": "Estimated CPC",
                "CommissionAmount": "Commission",
                "OpportunityScore": "Opportunity score",
                "SearchVolume": "Search volume",
            },
        )

        st.plotly_chart(
            chart,
            width="stretch",
        )

    display_columns = [
        "ProductID",
        "ProductName",
        "NetworkName",
        "Category",
        "Status",
        "Price",
        "CommissionAmount",
        "CommissionPercent",
        "EPC",
        "GravityScore",
        "SearchVolume",
        "EstimatedCPC",
        "CompetitionScore",
        "GoogleTrendScore",
        "RefundRate",
        "OpportunityScore",
        "MetricDate",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in products_df.columns
    ]

    st.dataframe(
        products_df[available_columns],
        hide_index=True,
        width="stretch",
    )

    csv_data = products_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Export products as CSV",
        data=csv_data,
        file_name="affiliate_products.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Delete a product")

    product_labels = {
        int(row["ProductID"]): (
            f'{row["ProductID"]} — '
            f'{row["ProductName"]}'
        )
        for _, row in products_df.iterrows()
    }

    product_to_delete = st.selectbox(
        "Select product",
        options=list(product_labels.keys()),
        format_func=lambda product_id: (
            product_labels[product_id]
        ),
    )

    confirm_delete = st.checkbox(
        (
            "I understand that this will delete the product "
            "and its related records."
        )
    )

    if st.button(
        "Delete selected product",
        type="secondary",
        disabled=not confirm_delete,
    ):
        try:
            deleted = repo.delete_product(
                int(product_to_delete)
            )

            if deleted:
                st.success(
                    "Product deleted."
                )
                st.rerun()

            else:
                st.warning(
                    "Product was not found."
                )

        except Exception as exc:
            st.exception(exc)