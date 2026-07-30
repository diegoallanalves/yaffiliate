from __future__ import annotations

from decimal import Decimal
from html import escape

import pandas as pd
import streamlit as st

from app.components.charts import metric_history_chart
from app.components.layout import page_header
from app.repositories.product_repository import ProductRepository
from app.services.opportunity_timeline_service import (
    OpportunityTimelineService,
)
from app.services.product_intelligence_service import (
    ProductIntelligenceService,
)
from app.services.trend_analysis_service import (
    TrendAnalysisService,
)


product_repository = ProductRepository()
intelligence_service = ProductIntelligenceService()
timeline_service = OpportunityTimelineService()
trend_analysis_service = TrendAnalysisService()


def to_float(value: object | None) -> float:
    """Convert SQL Server numeric values into Python floats."""
    if value is None:
        return 0.0

    if isinstance(value, Decimal):
        return float(value)

    return float(value)


def get_risk_icon(risk_level: str) -> str:
    """Return a visual indicator for the risk level."""
    risk_icons = {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🔴",
    }

    return risk_icons.get(risk_level, "⚪")


def get_opportunity_icon(
    opportunity_score: float,
) -> str:
    """Return a visual indicator for the opportunity score."""
    if opportunity_score >= 80:
        return "🟢"

    if opportunity_score >= 65:
        return "🟢"

    if opportunity_score >= 50:
        return "🟡"

    if opportunity_score >= 35:
        return "🟠"

    return "🔴"


def get_trend_icon(trend: str) -> str:
    """Return a visual indicator for the historical trend."""
    trend_icons = {
        "Improving strongly": "🚀",
        "Improving": "📈",
        "Stable": "➡️",
        "Declining": "📉",
        "Declining strongly": "⚠️",
        "Insufficient history": "🕒",
        "No data": "⚪",
    }

    return trend_icons.get(trend, "⚪")


def get_decision_verdict(
    opportunity_score: float,
    risk_level: str,
    recommended_channel: str,
    recommended_budget: float,
) -> tuple[str, str, str]:
    """Return the main commercial decision shown to the user."""
    if opportunity_score >= 80 and risk_level == "Low":
        return (
            "PRIORITISE THIS PRODUCT",
            "Strong opportunity with low risk.",
            (
                f"Start with {recommended_channel} and validate using "
                f"a test budget of R$ {recommended_budget:,.2f}."
            ),
        )

    if opportunity_score >= 65 and risk_level != "High":
        return (
            "TEST THIS PRODUCT",
            "Good opportunity, but validate before scaling.",
            (
                f"Use {recommended_channel} first and keep the initial "
                f"budget near R$ {recommended_budget:,.2f}."
            ),
        )

    if opportunity_score >= 50:
        return (
            "TEST CAUTIOUSLY",
            "Moderate opportunity with incomplete proof.",
            (
                f"Run a small {recommended_channel} test using no more than "
                f"R$ {recommended_budget:,.2f} before increasing spend."
            ),
        )

    return (
        "DO NOT PRIORITISE YET",
        "The current data does not justify meaningful investment.",
        (
            "Improve the offer data, demand signals or commission "
            "before testing."
        ),
    )


def prepare_timeline_dataframe(
    timeline: dict,
) -> pd.DataFrame:
    """Convert timeline history into a chart-ready DataFrame."""
    history = timeline.get("history") or []

    dataframe = pd.DataFrame(history)

    if dataframe.empty:
        return dataframe

    if "RecordedAt" in dataframe.columns:
        dataframe["RecordedAt"] = pd.to_datetime(
            dataframe["RecordedAt"],
            errors="coerce",
        )

    numeric_columns = [
        "OpportunityScore",
        "SearchVolume",
        "GoogleTrendScore",
        "CompetitionScore",
        "GravityScore",
        "EPC",
        "EstimatedCPC",
        "RefundRate",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

    dataframe = dataframe.dropna(
        subset=["RecordedAt"]
    )

    return dataframe.sort_values(
        by="RecordedAt",
        ascending=True,
    )


def render() -> None:
    page_header(
        "Product Intelligence",
        "Understand which affiliate products deserve your attention.",
        (
            "Select a saved product and review its latest metrics, "
            "recommendation, history and commercial potential."
        ),
    )

    try:
        products = product_repository.list_products()

    except Exception as exc:
        st.error(f"Unable to load products: {exc}")
        return

    if not products:
        st.info(
            "No products are available yet. "
            "Add one in Product Research first."
        )
        return

    product_labels = {
        int(product["ProductID"]): str(product["ProductName"])
        for product in products
    }

    selected_product_id = st.selectbox(
        "Select a product",
        options=list(product_labels.keys()),
        format_func=lambda product_id: product_labels[product_id],
    )

    try:
        intelligence = intelligence_service.get_product_intelligence(
            selected_product_id
        )

        timeline = timeline_service.get_product_timeline(
            selected_product_id
        )

        trend_analysis = trend_analysis_service.analyse(
            timeline
        )

    except Exception as exc:
        st.error(f"Unable to load product intelligence: {exc}")
        return

    if intelligence is None:
        st.warning("The selected product could not be loaded.")
        return

    product = intelligence["product"]
    latest_metric = intelligence["latest_metric"]
    latest_recommendation = intelligence["latest_recommendation"]

    product_name = str(
        product.get("ProductName") or "Unnamed product"
    )

    network_name = str(
        product.get("NetworkName") or "Not set"
    )

    category = str(
        product.get("Category") or "Not set"
    )

    status = str(
        product.get("Status") or "Not set"
    )

    commission_amount = to_float(
        product.get("CommissionAmount")
    )

    search_volume = 0
    trend_score = 0.0
    competition_score = 0.0
    opportunity_score = 0.0

    if latest_metric is not None:
        search_volume = int(
            latest_metric.get("SearchVolume") or 0
        )

        trend_score = to_float(
            latest_metric.get("GoogleTrendScore")
        )

        competition_score = to_float(
            latest_metric.get("CompetitionScore")
        )

        opportunity_score = to_float(
            latest_metric.get("OpportunityScore")
        )

    opportunity_level = "Not available"
    risk_level = "Not available"
    difficulty = "Not available"
    recommended_channel = "Not available"
    expected_roi = "Not available"
    recommended_budget = 0.0

    reasoning: list[str] = []
    actions: list[str] = []

    if latest_recommendation is not None:
        opportunity_level = str(
            latest_recommendation.get("OpportunityLevel")
            or "Not available"
        )

        risk_level = str(
            latest_recommendation.get("RiskLevel")
            or "Not available"
        )

        difficulty = str(
            latest_recommendation.get("Difficulty")
            or "Not available"
        )

        recommended_channel = str(
            latest_recommendation.get("RecommendedChannel")
            or "Not available"
        )

        expected_roi = str(
            latest_recommendation.get("ExpectedROI")
            or "Not available"
        )

        recommended_budget = to_float(
            latest_recommendation.get("RecommendedBudget")
        )

        reasoning = list(
            latest_recommendation.get("Reasoning") or []
        )

        actions = list(
            latest_recommendation.get("NextActions") or []
        )

    safe_product_name = escape(product_name)
    safe_network_name = escape(network_name)
    safe_category = escape(category)
    safe_status = escape(status)

    product_header_html = (
        '<div style="'
        'padding:1.4rem;'
        'border:1px solid rgba(255,255,255,0.10);'
        'border-radius:18px;'
        'background:rgba(18,28,48,0.72);'
        'margin-top:1rem;'
        'margin-bottom:1.25rem;'
        '">'
        '<div style="'
        'font-size:1.75rem;'
        'font-weight:700;'
        'margin-bottom:0.35rem;'
        '">'
        f'📦 {safe_product_name}'
        '</div>'
        '<div style="'
        'color:#a7b3c7;'
        'font-size:0.95rem;'
        '">'
        f'{safe_network_name} · {safe_category} · {safe_status}'
        '</div>'
        '</div>'
    )

    st.markdown(
        product_header_html,
        unsafe_allow_html=True,
    )

    verdict_title, verdict_summary, verdict_action = (
        get_decision_verdict(
            opportunity_score=opportunity_score,
            risk_level=risk_level,
            recommended_channel=recommended_channel,
            recommended_budget=recommended_budget,
        )
    )

    opportunity_icon = get_opportunity_icon(
        opportunity_score
    )

    decision_html = (
        '<div style="'
        'padding:1rem 1.2rem;'
        'border-left:4px solid #8b5cf6;'
        'border-radius:10px;'
        'background:rgba(139,92,246,0.08);'
        'margin-bottom:1.25rem;'
        '">'
        '<div style="'
        'font-size:0.8rem;'
        'font-weight:700;'
        'letter-spacing:0.08em;'
        'text-transform:uppercase;'
        'color:#a78bfa;'
        'margin-bottom:0.4rem;'
        '">'
        'FILTRIFY DECISION'
        '</div>'
        '<div style="'
        'font-size:1.35rem;'
        'font-weight:700;'
        'margin-bottom:0.5rem;'
        '">'
        f'{opportunity_icon} {escape(verdict_title)}'
        '</div>'
        '<div style="'
        'font-size:1rem;'
        'margin-bottom:0.35rem;'
        'color:#e5e7eb;'
        '">'
        f'{escape(verdict_summary)}'
        '</div>'
        '<div style="'
        'font-size:0.95rem;'
        'color:#cbd5e1;'
        '">'
        f'{escape(verdict_action)}'
        '</div>'
        '</div>'
    )

    st.markdown(
        decision_html,
        unsafe_allow_html=True,
    )

    score_col, commission_col, demand_col, trend_col = st.columns(4)

    score_col.metric(
        "Opportunity score",
        f"{opportunity_score:.1f}/100",
        opportunity_level,
    )

    commission_col.metric(
        "Commission",
        f"R$ {commission_amount:,.2f}",
    )

    demand_col.metric(
        "Monthly searches",
        f"{search_volume:,}",
    )

    trend_col.metric(
        "Google Trend",
        f"{trend_score:.0f}/100",
    )

    strategy_col, risk_col, roi_col, budget_col = st.columns(4)

    strategy_col.metric(
        "Recommended channel",
        recommended_channel,
    )

    risk_col.metric(
        "Risk",
        f"{get_risk_icon(risk_level)} {risk_level}",
    )

    roi_col.metric(
        "Expected ROI",
        expected_roi,
    )

    budget_col.metric(
        "Suggested test budget",
        f"R$ {recommended_budget:,.2f}",
    )

    st.progress(
        min(
            max(opportunity_score / 100, 0.0),
            1.0,
        )
    )

    st.caption(
        f"Competition: {competition_score:.0f}/100 · "
        f"Difficulty: {difficulty}"
    )

    st.subheader("Opportunity timeline")

    timeline_col1, timeline_col2, timeline_col3, timeline_col4 = (
        st.columns(4)
    )

    timeline_col1.metric(
        "Current score",
        f'{timeline["current_score"]:.1f}/100',
    )

    timeline_col2.metric(
        "Score change",
        f'{timeline["score_change"]:+.2f}',
    )

    timeline_col3.metric(
        "Trend",
        (
            f'{get_trend_icon(str(timeline["trend"]))} '
            f'{timeline["trend"]}'
        ),
    )

    timeline_col4.metric(
        "Snapshots",
        timeline["snapshot_count"],
    )

    timeline_df = prepare_timeline_dataframe(
        timeline
    )

    if timeline["snapshot_count"] < 2:
        st.info(
            "At least two historical snapshots are required "
            "to calculate meaningful analytics."
        )

    else:
        analytics_left, analytics_right = st.columns(2)

        with analytics_left:
            metric_history_chart(
                timeline_df,
                "OpportunityScore",
                "Opportunity Score",
                y_label="Score",
            )

            metric_history_chart(
                timeline_df,
                "SearchVolume",
                "Search Volume",
                y_label="Monthly searches",
            )

            metric_history_chart(
                timeline_df,
                "EPC",
                "Earnings per Click",
                y_label="EPC",
            )

            metric_history_chart(
                timeline_df,
                "GravityScore",
                "Gravity Score",
                y_label="Gravity",
            )

        with analytics_right:
            metric_history_chart(
                timeline_df,
                "GoogleTrendScore",
                "Google Trend Score",
                y_label="Trend score",
            )

            metric_history_chart(
                timeline_df,
                "CompetitionScore",
                "Competition Score",
                y_label="Competition",
            )

            metric_history_chart(
                timeline_df,
                "RefundRate",
                "Refund Rate",
                y_label="Refund rate %",
            )

            metric_history_chart(
                timeline_df,
                "EstimatedCPC",
                "Estimated CPC",
                y_label="CPC",
            )

    st.subheader("Trend analyst")

    if trend_analysis["status"] == "Insufficient history":
        st.info(
            trend_analysis["headline"]
        )

        st.write(
            trend_analysis["summary"]
        )

        st.markdown("#### Recommendation")

        st.write(
            trend_analysis["recommendation"]
        )

    else:
        analyst_icon = get_trend_icon(
            str(trend_analysis["status"])
        )

        st.markdown(
            f"### {analyst_icon} {trend_analysis['headline']}"
        )

        st.write(
            trend_analysis["summary"]
        )

        analyst_col1, analyst_col2, analyst_col3 = st.columns(3)

        analyst_col1.metric(
            "Improving signals",
            f"{trend_analysis['improving_signals']}/7",
        )

        analyst_col2.metric(
            "Score movement",
            f"{trend_analysis['score_change']:+.2f}",
        )

        analyst_col3.metric(
            "Market status",
            trend_analysis["status"],
        )

        st.markdown("#### What changed")

        changes = trend_analysis.get("changes") or []

        for change in changes:
            if change.startswith("Positive:"):
                st.success(
                    change.replace(
                        "Positive: ",
                        "",
                        1,
                    )
                )

            elif change.startswith("Negative:"):
                st.warning(
                    change.replace(
                        "Negative: ",
                        "",
                        1,
                    )
                )

            else:
                st.info(change)

        st.markdown("#### Recommendation")

        st.write(
            trend_analysis["recommendation"]
        )

    if timeline["snapshot_count"] >= 2:
        if timeline["score_change"] > 0:
            st.success(
                (
                    f'The opportunity score has improved by '
                    f'{timeline["score_change"]:.2f} points, from '
                    f'{timeline["first_score"]:.2f} to '
                    f'{timeline["current_score"]:.2f}.'
                )
            )

        elif timeline["score_change"] < 0:
            st.warning(
                (
                    f'The opportunity score has declined by '
                    f'{abs(timeline["score_change"]):.2f} points, from '
                    f'{timeline["first_score"]:.2f} to '
                    f'{timeline["current_score"]:.2f}.'
                )
            )

        else:
            st.info(
                "The opportunity score has remained stable."
            )

    st.caption(
        (
            f'Highest historical score: '
            f'{timeline["highest_score"]:.2f} · '
            f'Lowest historical score: '
            f'{timeline["lowest_score"]:.2f}'
        )
    )

    st.divider()

    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Why this product")

        if latest_recommendation is None:
            st.info(
                "No saved recommendation is available."
            )

        elif not reasoning:
            st.info(
                "No recommendation reasoning is available."
            )

        else:
            for reason in reasoning:
                st.markdown(
                    f"✓ {reason}"
                )

    with right_column:
        st.subheader("Recommended next actions")

        if latest_recommendation is None:
            st.info(
                "No saved next actions are available."
            )

        elif not actions:
            st.info(
                "No next actions are available."
            )

        else:
            for index, action in enumerate(
                actions,
                start=1,
            ):
                st.markdown(
                    f"**{index}.** {action}"
                )