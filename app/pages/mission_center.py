from __future__ import annotations

import streamlit as st

from app.components.layout import page_header

from app.collectors.hotmart_collector import (
    HotmartCollector,
)

from app.services.comparison_service import (
    ComparisonService,
)

from app.services.product_analysis_service import (
    ProductAnalysisService,
)

from app.services.mission_plan_service import (
    MissionPlanService,
)


collector = HotmartCollector()

comparison_service = ComparisonService()

analysis_service = ProductAnalysisService()

mission_service = MissionPlanService()


def render() -> None:

    page_header(
        "Mission Center",
        "Your affiliate execution dashboard.",
        (
            "Turn product intelligence into daily "
            "actions."
        ),
    )

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=5,
    )

    comparison = comparison_service.compare(
        products
    )

    selected_product = products[0]

    selected_comparison = next(
        item
        for item in comparison.products
        if item.product.product_name
        == selected_product.product_name
    )

    analysis = analysis_service.analyse(
        product=selected_product,
        comparison=selected_comparison,
    )

    mission = mission_service.generate(
        product=selected_product,
        analysis=analysis,
    )

    st.success(
        f"Today's mission: {mission.mission_title}"
    )

    progress = (
        sum(
            task.completed
            for task in mission.tasks
        )
        / len(mission.tasks)
    )

    st.progress(progress)

    col1, col2 = st.columns(2)

    col1.metric(
        "Tasks",
        len(mission.tasks),
    )

    col2.metric(
        "Estimated Time",
        f"{mission.estimated_total_minutes} min",
    )

    st.divider()

    st.subheader("Mission Tasks")

    for task in mission.tasks:

        st.checkbox(
            f"{task.title} ({task.estimated_minutes} min)",
            value=task.completed,
        )

        st.caption(task.description)